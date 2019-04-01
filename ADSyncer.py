import logging
import logging.handlers
from BufferingSMTPHandler import BufferingSMTPHandler
from Settings import DATA_SOURCE_FILE, \
    IMPORT_CHUNK_SIZE, AD_DC, AD_USERNAME, AD_PASSWORD, AD_OU_ASSIGNMENTS, \
    AD_ATTRIBUTE_MAP, AD_GROUP_ASSIGNMENTS, DS_COLUMN_DEFINITION, \
    AD_STUDENT_USERNAME_FIELDS, AD_STUDENT_USERNAME_FORMATS, \
    AD_STAFF_USERNAME_FIELDS, AD_STAFF_USERNAME_FORMATS, AD_BASE_USER_DN, \
    DS_ACCOUNT_IDENTIFIER, TARGET_ACCOUNT_IDENTIFIER, DATA_SOURCE_FILE_TYPE
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
                                     TARGET_ACCOUNT_IDENTIFIER,
                                     AD_OU_ASSIGNMENTS,
                                     AD_ATTRIBUTE_MAP,
                                     AD_GROUP_ASSIGNMENTS,
                                     IMPORT_CHUNK_SIZE) as adam:
                self._logger.debug("end accountmanager init")

                # Sync Process
                # For each user in adam.data...
                for rowid in adam.data:
                    # Are they linked to a user in AD (by their provided ID)?
                    dsusr = adam.dataRow(rowid)
                    userid = dsusr[adam.dataColumns(DS_ACCOUNT_IDENTIFIER)]
                    adusr = adam.getLinkedUserInfo(userid,
                                                   [i.mappedAttribute
                                                    for i in AD_ATTRIBUTE_MAP])

                    if adusr is not None:  # If so,
                        # we will check for any necessary updates*
                        self._syncAttributes(dsusr, adusr)
                        #print(fn + " " + ln + ": " + str(adusr))

                    else:  # If not,
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
        self._logger.info("Sync Process has completed.")
        # End Script

    def _syncAttributes(self, dsUsr: tuple, adUsr: dict):
        """
        Synchronizes the appropriate attributes from the datasource to target
        """
        for itm in AD_ATTRIBUTE_MAP:
            # get the current AD attribute value
            adusr_attr_val = adUsr.get(itm.mappedAttribute)
            # get the current data source attribute value
            ds_attr_val = dsUsr[DS_COLUMN_DEFINITION.get(itm.sourceColumnName)]
            self._logger.debug("Data Source :: "
                               + itm.sourceColumnName
                               + " = " + str(ds_attr_val))
            self._logger.debug("AD :: "
                               + itm.mappedAttribute
                               + " = " + str(adusr_attr_val))
