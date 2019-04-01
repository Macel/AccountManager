import logging
import logging.handlers
from BufferingSMTPHandler import BufferingSMTPHandler
from Settings import DATA_SOURCE_FILE, \
    IMPORT_CHUNK_SIZE, AD_DC, AD_USERNAME, AD_PASSWORD, AD_OU_ASSIGNMENTS, \
    AD_ATTRIBUTE_MAP, AD_GROUP_ASSIGNMENTS, DS_COLUMN_DEFINITION, \
    AD_STUDENT_USERNAME_FIELDS, AD_STUDENT_USERNAME_FORMATS, \
    AD_STAFF_USERNAME_FIELDS, AD_STAFF_USERNAME_FORMATS, AD_BASE_USER_DN, \
    DS_ACCOUNT_IDENTIFIER, AD_TARGET_ACCOUNT_IDENTIFIER, DATA_SOURCE_FILE_TYPE, \
    DS_STATUS_ACTIVE_VALUE, DS_STATUS_INACTIVE_VALUE, DS_STATUS_COLUMN_NAME
from AccountManager import AccountManager  # for atom code completion
from AccountManager_Module_AD.ADAccountManager import \
    GetADAccountManager
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
                                     AD_GROUP_ASSIGNMENTS,
                                     IMPORT_CHUNK_SIZE) as self._adam:
                self._logger.debug("end accountmanager init")

                # Begin sync process for current page of users.

                # For each user in adam.data...
                for rowid in self._adam.data:
                    dsusr = self._adam.dataRow(rowid)
                    userid = dsusr[self._adam.dataColumns(DS_ACCOUNT_IDENTIFIER)]
                    adusr = self._adam.getLinkedUserInfo(userid,
                                                         [i.mappedAttribute
                                                          for i in AD_ATTRIBUTE_MAP])
                    # Are they linked to a user in AD (by their provided ID)?
                    if adusr is not None:  # If so,
                        # Sync any updated information
                        self._logger.debug("Linked user found for id: " + userid
                                           + ".  Syncing information.")
                        self._syncOU(userid, dsusr, adusr)
                        self._syncActiveStatus(userid, dsusr, adusr)
                        # Don't bother syncing attributes/group membership if
                        # the user is not active.
                        if (dsusr[self._adam.dataColumns(DS_STATUS_COLUMN_NAME)]
                            == DS_STATUS_ACTIVE_VALUE):
                            self._logger.debug(userid + " is active, syncing attributes"
                                               + " and group membership.")
                            self._syncAttributes(userid, dsusr, adusr)
                            self._syncGroupMembership(userid, dsusr, adusr)


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

    def _syncGroupMembership(self, userid, dsusr: dict, adusr: dict):
        """
        Ensure that the provided user is a member of all the correct
        synchronized groups and not in any synchronized groups to which they
        are not assigned.
        """
        self._logger.debug("Would sync Group Membership now...")
        # TODO: Implement
        pass

    def _syncOU(self, userid, dsusr: dict, adusr: dict):
        """
        Ensure that the provided user is placed into the correct OU based on
        their membership rules.
        """
        self._logger.debug("Would sync OU now...")
        # TODO: Implement
        pass

    def _syncActiveStatus(self, userid, dsusr: dict, adusr: dict):
        """
        Set the user to enabled or disabled in AD based on the datasource
        active/inactive status.
        """
        self._logger.debug("Would sync Active Status now...")
        # TODO: implement
        pass

    def _syncAttributes(self, userid, dsusr: dict, adusr: dict):
        """
        Synchronizes the appropriate attributes from the datasource to target
        """
        for itm in AD_ATTRIBUTE_MAP:
            # If the item is intended to be kept synchronized,
            if (itm.synchronized):
                # get the current data source attribute value
                ds_attr_val = dsusr[DS_COLUMN_DEFINITION.get(itm.sourceColumnName)]
                # get the current AD attribute value
                adusr_attr_val = adusr.get(itm.mappedAttribute)

                if ds_attr_val != adusr_attr_val:
                    self._logger.debug("Found mismatch between datasource and AD attribute: "
                                       + itm.mappedAttribute + "DS: " + str(ds_attr_val)
                                       + "AD: " + str(adusr_attr_val) + ". "
                                       + "Setting AD attribute to DS value.")
                    self._adam.setAttribute(userid, itm.mappededAttribute, str(ds_attr_val))
