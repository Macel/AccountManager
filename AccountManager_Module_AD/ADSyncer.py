import logging
import logging.handlers
from BufferingSMTPHandler import BufferingSMTPHandler
from Settings import DATA_SOURCE_FILE, \
    IMPORT_CHUNK_SIZE, AD_DC, AD_USERNAME, AD_PASSWORD, AD_OU_ASSIGNMENTS, \
    AD_ATTRIBUTE_MAP, AD_GROUP_ASSIGNMENTS, DS_COLUMN_DEFINITION, \
    AD_STUDENT_USERNAME_FIELDS, AD_STUDENT_USERNAME_FORMATS, \
    AD_STAFF_USERNAME_FIELDS, AD_STAFF_USERNAME_FORMATS, AD_BASE_USER_DN, \
    DS_ACCOUNT_IDENTIFIER, AD_TARGET_ACCOUNT_IDENTIFIER, DATA_SOURCE_FILE_TYPE, \
    DS_STATUS_ACTIVE_VALUES, DS_STATUS_INACTIVE_VALUES, DS_STATUS_COLUMN_NAME, \
    AD_DEFAULT_USER_OU
from AccountManager import AccountManager  # for atom code completion
from AccountManager_Module_AD.ADAccountManager import \
    GetADAccountManager
from AccountManager_Module_AD.ADOrgUnitAssignments import ADOrgUnitAssignment
from CSVPager import CSVPager


class ADSyncer():
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def runSyncProcess(self):
        """
        Initiates the sync process.
        References the common and AD-related settings in Settings.py
        """
        # Sync accounts on paged data.
        pager = CSVPager(DATA_SOURCE_FILE,
                         DATA_SOURCE_FILE_TYPE,
                         IMPORT_CHUNK_SIZE,
                         DS_COLUMN_DEFINITION.get(DS_ACCOUNT_IDENTIFIER))
        self._logger.debug("pager total record count: " + str(pager.csvRecordCount))
        i = 0
        while True:
            # With each page of records from the CSV file, run the sync process
            i = pager.getPage(i)
            currentPage = pager.page

            # With the current page, use ADAccountManager to sync data to AD
            self._logger.debug("begin accountmanager init")
            with GetADAccountManager(AD_DC, AD_USERNAME, AD_PASSWORD,
                                     AD_BASE_USER_DN,
                                     currentPage,
                                     DS_COLUMN_DEFINITION,
                                     DS_ACCOUNT_IDENTIFIER,
                                     AD_TARGET_ACCOUNT_IDENTIFIER,
                                     AD_OU_ASSIGNMENTS,
                                     AD_ATTRIBUTE_MAP,
                                     securityGroupAssignments=AD_GROUP_ASSIGNMENTS,
                                     maxSize=IMPORT_CHUNK_SIZE) as self._adam:
                self._logger.debug("end accountmanager init")

                # Begin sync process for current page of users.

                # For each user in adam.data...
                for rowid in self._adam.data:
                    dsusr = self._adam.dataRow(rowid)
                    linkid = dsusr[DS_ACCOUNT_IDENTIFIER]
                    adusr = self._adam.getLinkedUserInfo(linkid,
                                                         *[atr.mappedAttribute
                                                          for atr in AD_ATTRIBUTE_MAP])
                    # Are they linked to a user in AD (by their provided ID)?
                    if adusr is not None:  # If so,
                        # Sync any updated information
                        self._logger.debug("Linked user found for id: " + linkid
                                           + ".  Syncing information.")
                        # Don't bother syncing attributes/group membership if
                        # the user is not active.
                        if (dsusr[DS_STATUS_COLUMN_NAME]
                            in set(DS_STATUS_ACTIVE_VALUES)):

                            self._logger.debug(linkid + " is active, syncing attributes"
                                               + " and group membership.")
                            self._syncAttributes(dsusr, adusr)
                            self._syncGroupMembership(dsusr, adusr)
                        else:
                            self._logger.debug(linkid + " is not active, will not bother"
                                               + " syncing attributes/group membership.")

                        self._logger.debug(linkid + ": Syncing active status.")
                        self._syncActiveStatus(dsusr, adusr)

                        # Sync the OU last because if a user's OU changes,
                        # the OU information in adusr will become invalid.
                        self._logger.debug(linkid + ": Syncing OU.")
                        self._syncOU(dsusr, adusr)
                    else:  # TODO: If not,
                        pass
                        #print("AD user not found for: " + fn + " " + ln)
                        # configured secondary field matches? (such as email)
                        # secondary match found,
                            # link the user by updating their ID in AD
                            # we will check for any necessary updates*
                        # No secondary match found,
                            # User has an OU assignment rule?
                            # If not,
                                # don't bother creating the user and log it
                            # If so,
                                # create the user and apply any matching OU and group rules

            if i == -1:  # End of CSV file reached
                break
            self._logger.info("AD Sync Process complete.")

    def _syncGroupMembership(self, dsusr: dict, adusr: dict):
        """
        Ensure that the provided user is a member of all the correct
        synchronized groups and not in any synchronized groups to which they
        are not assigned.
        """

        linkid = dsusr[DS_ACCOUNT_IDENTIFIER]
        self._logger.info(linkid + ": Syncing group membership")
        # TODO: Implement
        pass

    def _syncOU(self, dsusr: dict, adusr: dict):
        """
        Ensure that the provided user is placed into the correct OU based on
        their membership rules.
        """
        linkid = dsusr[DS_ACCOUNT_IDENTIFIER]
        self._logger.info(linkid + ": Syncing OU assignments")

        for ou in AD_OU_ASSIGNMENTS:
            ruleMatchCount = ou.ruleMatchCount(dsusr)
            if ou.matchMethod == ADOrgUnitAssignment.MATCH_ANY_RULE:
                if ruleMatchCount > 0:
                    self._logger.debug(linkid + ": Matching org unit found: "
                                       + ou.orgUnitDN)
                    if (self._adam.setUserOU(linkid, ou.orgUnitDN)):
                        self._logger.info(linkid + ": Moved to " + ou.orgUnitDN)
                    return
            elif ou.matchMethod == ADOrgUnitAssignment.MATCH_ALL_RULES:
                if ruleMatchCount == len(ou.rules):
                    self._logger.debug(linkid + ": Matching org unit found: "
                                       + ou.orgUnitDN)
                    if (self._adam.setUserOU(linkid, ou.orgUnitDN)):
                        self._logger.info(linkid + ": Moved to " + ou.orgUnitDN)
                    return

        # It appears there were no OU matches for this user.  Set their OU to
        # the default OU specified in settings.
        self._logger.debug(linkid + ": No OU assignments found. Assigning "
                           + "default OU.")
        if (self._adam.setUserOU(linkid, AD_DEFAULT_USER_OU)):
            self._logger.info(linkid + ": No longer matches any OU Assignments."
                              + " User moved to default OU ("
                              + AD_DEFAULT_USER_OU + ")")

    def _syncActiveStatus(self, dsusr: dict, adusr: dict):
        """
        Set the user to enabled or disabled in AD based on the datasource
        active/inactive status.
        """
        linkid = dsusr[DS_ACCOUNT_IDENTIFIER]
        status = dsusr[DS_STATUS_COLUMN_NAME]
        if status in DS_STATUS_ACTIVE_VALUES:
            self._adam.setUserEnabled(linkid, True)
        else:
            self._adam.setUserEnabled(linkid, False)

    def _syncAttributes(self, dsusr: dict, adusr: dict):
        """
        Synchronizes the mapped attributes (marked to be synchronized)
        from the datasource to target.
        """
        linkid = dsusr[DS_ACCOUNT_IDENTIFIER]
        self._logger.info(linkid + ": Syncing Attributes")
        for itm in AD_ATTRIBUTE_MAP:
            # If the item is intended to be kept synchronized,
            if (itm.synchronized):
                # get the current data source attribute value
                ds_attr_val = dsusr[itm.sourceColumnName]
                # get the current AD attribute value
                adusr_attr_val = adusr[itm.mappedAttribute]

                if ds_attr_val != adusr_attr_val:
                    self._logger.debug("Found mismatch between datasource and AD attribute: "
                                       + itm.mappedAttribute + " DS: " + str(ds_attr_val)
                                       + " AD: " + str(adusr_attr_val) + ". "
                                       + "Setting AD attribute to DS value.")
                    self._adam.setAttribute(linkid, itm.mappedAttribute,
                                            str(ds_attr_val))
