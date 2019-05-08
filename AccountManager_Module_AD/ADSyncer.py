import logging
import logging.handlers
import re
from BufferingSMTPHandler import BufferingSMTPHandler
from Settings import \
    IMPORT_CHUNK_SIZE, DATA_SOURCE_FILE, DS_COLUMN_DEFINITION, \
    DATA_SOURCE_FILE_TYPE, DS_ACCOUNT_IDENTIFIER, DS_STATUS_ACTIVE_VALUES, \
    DS_STATUS_INACTIVE_VALUES, DS_STATUS_COLUMN_NAME, DS_SECONDARY_MATCH_COLUMN, \
    DS_USERNAME_COLUMN_NAME, DS_PASSWORD_COLUMN_NAME, \
    AD_DC, AD_USERNAME, AD_PASSWORD, AD_BASE_USER_DN, AD_OU_ASSIGNMENTS, \
    AD_ATTRIBUTE_MAP, AD_GROUP_ASSIGNMENTS, AD_TARGET_ACCOUNT_IDENTIFIER, \
    AD_DEFAULT_USER_OU, AD_SECONDARY_MATCH_ATTRIBUTE, AD_SHOULD_GENERATE_USERNAME, \
    AD_SHOULD_GENERATE_PASSWORD, USERNAME_ASSIGNMENTS, STUDENT_USERNAME_FIELDS, \
    STUDENT_USERNAME_FORMATS, STAFF_USERNAME_FIELDS, STAFF_USERNAME_FORMATS, \
    PASSWORD_ASSIGNMENTS, NEW_USER_NOTIFICATIONS, SMTP_SERVER_IP, SMTP_SERVER_PORT, \
    SMTP_FROM_ADDRESS, SMTP_SERVER_PASSWORD, SMTP_SERVER_USERNAME, \
    AD_USER_NOTIFICATION_MSG, AD_USER_NOTIFICATION_SUBJECT, \
    SHOULD_GENERATE_ACCOUNT_INFO_FILE, ACCOUNT_INFO_FILE_PATH, \
    ACCOUNT_INFO_FILE_FIELDS

from AccountManager import AccountManager  # for atom code completion
from AccountManager_Module_AD.ADAccountManager import \
    GetADAccountManager
from AccountManager_Module_AD.ADOrgUnitAssignments import ADOrgUnitAssignment
from CSVPager import CSVPager
from Exceptions import NoFreeUserNamesException, \
                       UserNameInvalidFieldDataException, \
                       PasswordNotSetException
from PasswordAssignments import PasswordAssignment
from NewUserNotifications import NewUserNotification
from smtplib import SMTP, SMTPException
from email.mime.text import MIMEText
import csv
import datetime


# Define any characters that should be excluded from newly generated usernames
# for AD.
AD_USERNAME_INVALID_CHARS = "/\\[]:;|=+*?<>\"@. "


class ADSyncer():
    # TODO: Make this an implementation of abstract class, AccountSyncer
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
        notify_emails = {}
        while True:
            # With each page of records from the CSV file, run the sync process
            i = pager.getPage(i)
            currentPage = pager.page
            output_data = []  # Will contain data for any new users that will be
                              # written to the output CSV (if setting enabled)

            # With the current page, use ADAccountManager to sync data to AD
            self._logger.debug("begin accountmanager init")
            with GetADAccountManager(AD_DC, AD_USERNAME, AD_PASSWORD,
                                     AD_BASE_USER_DN,
                                     currentPage,
                                     DS_COLUMN_DEFINITION,
                                     DS_ACCOUNT_IDENTIFIER,
                                     AD_TARGET_ACCOUNT_IDENTIFIER,
                                     AD_SECONDARY_MATCH_ATTRIBUTE,
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
                    # TODO: Error Handling
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
                            # TODO: Error Handling
                            self._syncAttributes(dsusr, adusr)
                            # TODO: Error Handling
                            self._syncGroupMembership(dsusr, adusr)
                        else:
                            self._logger.debug(linkid + " is not active, will not bother"
                                               + " syncing attributes/group membership.")

                        self._logger.debug(linkid + ": Syncing active status.")
                        # TODO: Error Handling
                        self._syncActiveStatus(dsusr, adusr)

                        # Sync the OU last because if a user's OU changes,
                        # the OU information in adusr will become invalid.
                        self._logger.debug(linkid + ": Syncing OU.")
                        self._syncOU(dsusr, adusr)
                    else:  # Linked user not found...
                        # See if a user exists with a match in the secondary field.
                        if (dsusr[DS_SECONDARY_MATCH_COLUMN] is not None
                            and len(dsusr[DS_SECONDARY_MATCH_COLUMN])) > 0:
                            # Don't match on an empty secondary field.
                            # TODO: Error Handling
                            adusr = self._adam.getUserInfo(AD_SECONDARY_MATCH_ATTRIBUTE,
                                                           dsusr[DS_SECONDARY_MATCH_COLUMN],
                                                           *[atr.mappedAttribute
                                                             for atr in AD_ATTRIBUTE_MAP])
                        else:
                            adusr = None
                        if adusr is not None:
                            # Secondary match found,
                            # link the user by updating their ID in AD
                            # we will check for any necessary updates*
                            # Sync any updated information
                            self._logger.debug("Secondary match found for '"
                                               + AD_SECONDARY_MATCH_ATTRIBUTE
                                               + "'': " + dsusr[DS_SECONDARY_MATCH_COLUMN]
                                               + ".  Linking user and syncing information.")

                            # TODO: Error Handling
                            self._adam.linkUser(dsusr[DS_SECONDARY_MATCH_COLUMN],
                                                linkid)
                            self._logger.info(linkid + ": An unlinked AD user has been found with"
                                              + " a matching secondary attribute and linked.")
                            # Don't bother syncing attributes/group membership if
                            # the user is not active.
                            if (dsusr[DS_STATUS_COLUMN_NAME]
                                in set(DS_STATUS_ACTIVE_VALUES)):
                                self._logger.debug(linkid + " is active, syncing attributes"
                                                   + " and group membership.")
                                # TODO: Error Handling
                                self._syncAttributes(dsusr, adusr)
                                # TODO: Error Handling
                                self._syncGroupMembership(dsusr, adusr)
                            else:
                                self._logger.debug(linkid + " is not active, will not bother"
                                                   + " syncing attributes/group membership.")

                            self._logger.debug(linkid + ": Syncing active status.")
                            # TODO: Error Handling
                            self._syncActiveStatus(dsusr, adusr)
                            # Sync the OU last because if a user's OU changes,
                            # the OU information in adusr will become invalid.
                            self._logger.debug(linkid + ": Syncing OU.")
                            # TODO: Error Handling
                            self._syncOU(dsusr, adusr)
                        else:
                            # No secondary match found,
                            # User is active?
                            if (dsusr[DS_STATUS_COLUMN_NAME]
                                in set(DS_STATUS_ACTIVE_VALUES)):
                                ### Create the user ###
                                # Grab password for new user and set the
                                # forcepwdchg flag accordingly
                                if AD_SHOULD_GENERATE_PASSWORD:
                                    pa = self._getPasswordAssignment(dsusr)
                                    if pa is None:
                                        self._logger.error(linkid + ": Could not find a matching password assignment method for "
                                                           + "new user.  Will not be able to create a new user account "
                                                           + "until this is resolved.")
                                        continue
                                    else:
                                        passwd = pa.getPass()
                                        forcepwdchg = pa.usermustreset
                                else:
                                    try:
                                        passwd = dsusr[DS_PASSWORD_COLUMN_NAME]
                                        forcepwdchg = True
                                    except Exception:
                                        self._logger.error(linkid + "The datasource does not appear to have a password column, but "
                                                           + "AD_SHOULD_GENERATE_PASSWORD is not set.  Cannot create user until "
                                                           + "this is resolved.")
                                        continue

                                self._logger.debug(linkid + ": Is active, but was not found in AD. "
                                                   + "Will attempt to create a new AD account for this user.")
                                try:
                                    upn = self._createUser(dsusr)
                                except Exception as e:
                                    self._logger.error(linkid + ": An error occurred attempting to "
                                                       + "create new AD user account. Will attempt creation "
                                                       + "again on the next sync.  Message: " + str(e.args[0]))
                                    continue
                                # Now that the user is created, grab the adusr info
                                # TODO: Error Handling
                                adusr = self._adam.getLinkedUserInfo(linkid,
                                                                     *[atr.mappedAttribute
                                                                      for atr in AD_ATTRIBUTE_MAP])
                                # Set additional attributes for the user per
                                # the attribute map...
                                # TODO: Error Handling
                                self._syncAttributes(dsusr, adusr, syncall=True)
                                # Join the user to any groups
                                # TODO: Error Handling
                                self._syncGroupMembership(dsusr, adusr, syncall=True)

                                try:
                                    self._adam.setUserPassword(linkid, passwd)
                                except PasswordNotSetException as pe:
                                    # A problem occurred setting the password.
                                    errmsg = linkid + ": Attempting to set password for new user failed. "
                                    # Delete the user so creation will be re-attempted.
                                    try:
                                        self._adam.deleteUser(linkid)

                                    except Exception as e:
                                        errmsg += "Additionally, user deletion was attempted so the password " \
                                                  + "set would be attempted on the next sync, but deletion also failed. " \
                                                  + "This user will have to be manually deleted from AD, or their " \
                                                  + "account will need to have a password set and activated manually. " \
                                                  + " ...  User deletion failure details: " + str(e)
                                    errmsg += "User will be deleted, and creation will be attempted again on the next sync." \
                                              + "Password set failure details: " + str(pe)
                                    self._logger.error(errmsg)
                                    continue
                                # TODO: Error Handling
                                self._syncActiveStatus(dsusr, adusr)

                                # Force a password change if the flag is set.
                                if forcepwdchg:
                                    self._logger.debug(linkid + ": Will be forced to change password on next login")
                                    # TODO: Error Handling
                                    self._adam.forcePasswordChange(linkid)

                                self._logger.info(linkid + ": New account has been created.  dn: "
                                                  + adusr["distinguishedName"][0])
                                # Append the new user to a data structure which will be output to the accountinfo csv file
                                # (if this option is enabled)
                                if SHOULD_GENERATE_ACCOUNT_INFO_FILE:
                                    output_data.append([datetime.datetime.now(), upn, passwd] + [self._adam.dataRow(linkid)[col]
                                     for col in ACCOUNT_INFO_FILE_FIELDS])
                                # If this new user has a notification assignment, add the notification to the new user notifications list.
                                for notification in NEW_USER_NOTIFICATIONS:
                                    if notification.match(dsusr):
                                        new_account_info = "Username: " + upn + ", " + ", ".join(
                                            [col + ": " + self._adam.dataRow(linkid)[col]
                                             for col in ACCOUNT_INFO_FILE_FIELDS])
                                        if notification.contacts in notify_emails:
                                            notify_emails[notification.contacts] += [new_account_info]
                                        else:
                                            notify_emails[notification.contacts] = [new_account_info]
                            else:
                                # user is not active anyway, don't bother creating the user
                                self._logger.debug(linkid + ": is not active, so will not bother creating a new account for this user.")
                if (len(output_data) > 0):
                    # If there is new user data to output to CSV, write it now.
                    # TODO: Error Handling
                    with open(ACCOUNT_INFO_FILE_PATH, mode='a') as output_file:
                        writer = csv.writer(output_file, delimiter=",", quotechar="\"", quoting=csv.QUOTE_ALL)
                        writer.writerows(output_data)

            if i == -1:  # End of CSV file reached
                # Send out new user account notifications
                self._sendNewUserNotifications(notify_emails)
                self._logger.info("AD Sync Process complete.")
                break

    def _sendNewUserNotifications(self, notifications: dict):
        """
        Takes a dictionary of the form { email-addresses : < new user info string > }
        and sends notifications for each entry in the dictionary.
        """
        for recpts in notifications.keys():
            recipients = ",".join(map(str, recpts))
            subject = AD_USER_NOTIFICATION_SUBJECT
            body = (
                    AD_USER_NOTIFICATION_MSG
                    + "\n" + "\n".join(notifications[recpts])
                   )
            msg = MIMEText(body)
            msg['From'] = SMTP_FROM_ADDRESS
            msg['To'] = recipients
            msg['Subject'] = subject
            try:
                server = SMTP(SMTP_SERVER_IP, SMTP_SERVER_PORT)
                server.send_message(msg)
            except SMTPException as e:
                self._logger.error("A problem occurred while attempting to send out a new user notification email. "
                                   + "Error details as follows: " + str(e))
            print("new account notification msg: " + str(msg))

    def _syncGroupMembership(self, dsusr: dict, adusr: dict, syncall: bool = False):
        """
        Ensure that the provided user is a member of all the correct
        synchronized groups and not in any synchronized groups to which they
        are not assigned.
        """

        linkid = dsusr[DS_ACCOUNT_IDENTIFIER]

        syncedgrps = [grp for grp in AD_GROUP_ASSIGNMENTS if
                      (grp.synchronized or syncall)]
        matchedgrps = [grp.groupDN for grp in syncedgrps if grp.match(dsusr)]
        nomatchedgrps = [grp.groupDN for grp in syncedgrps
                         if not grp.match(dsusr)]

        # First ensure that the user is assigned to any synced groups whose
        # rules they match.
        # TODO: Error Handling
        result = self._adam.assignUserGroups(linkid, *matchedgrps)
        if len(result) > 0:
            self._logger.info(linkid + ": was added to the following group(s): "
                              + str(result))

        # Now verify that the user is not in any synchronized groups that
        # they do *not* match the rules for....
        # TODO: Error Handling
        result = self._adam.deassignUserGroups(linkid, *nomatchedgrps)
        if len(result) > 0:
            self._logger.info(linkid + ": was removed from the following "
                              + "group(s): " + str(result))

    def _syncOU(self, dsusr: dict, adusr: dict):
        """
        Ensure that the provided user is placed into the correct OU based on
        their membership rules. Note that if a user matches more than one OU
        assignment, they will get placed into the first matching org unit found.
        """
        linkid = dsusr[DS_ACCOUNT_IDENTIFIER]
        destination_ou = None

        for ou in AD_OU_ASSIGNMENTS:
            if ou.match(dsusr):
                self._logger.debug(linkid + ": Matching org unit found: "
                                   + ou.orgUnitDN)
                destination_ou = ou.orgUnitDN
                break
        if destination_ou is None:
            # It appears there were no OU matches for this user.  Set their OU to
            # the default OU specified in settings.
            destination_ou = AD_DEFAULT_USER_OU
            self._logger.debug(linkid + ": No OU assignments found. Assigning "
                               + "default OU.")
        # TODO: Error Handling
        if (self._adam.setUserOU(linkid, destination_ou)):
            self._logger.info(linkid + ": Moved to " + destination_ou)

    def _syncActiveStatus(self, dsusr: dict, adusr: dict):
        """
        Set the user to enabled or disabled in AD based on the datasource
        active/inactive status.
        """
        linkid = dsusr[DS_ACCOUNT_IDENTIFIER]
        status = dsusr[DS_STATUS_COLUMN_NAME]
        if status in DS_STATUS_ACTIVE_VALUES:
            if (self._adam.setUserEnabled(linkid, True)):
                self._logger.info(linkid + ": Has been re-enabled.")
        else:
            if (self._adam.setUserEnabled(linkid, False)):
                self._logger.info(linkid + ": Has been disabled.")

    def _syncAttributes(self, dsusr: dict, adusr: dict, syncall: bool = False):
        """
        Synchronizes the mapped attributes (marked to be synchronized)
        from the datasource to target.

        dsusr: dictionary of data for the user from the datasource in the form
        { field: data }
        adusr: dictionary of data for the linked AD user in the form
        { field: data }

        syncall: setting this flag to true forces synchronization of all
        attributes, even if they are not marked as SYNCHRONIZED.

        Note: synced attributes are assumed to be single-valued
        """
        linkid = dsusr[DS_ACCOUNT_IDENTIFIER]
        for itm in AD_ATTRIBUTE_MAP:
            # If the item is intended to be kept synchronized,
            if itm.synchronized or syncall:
                # get the current data source attribute value
                ds_attr_val = dsusr[itm.sourceColumnName]
                # get the current AD attribute value
                if not adusr[itm.mappedAttribute] is None:
                    adusr_attr_val = adusr[itm.mappedAttribute][0]
                else:
                    adusr_attr_val = None

                if ds_attr_val != adusr_attr_val:
                    self._logger.info(linkid + ": AD attribute mismatch for '"
                                       + itm.mappedAttribute + "', DS: " + str(ds_attr_val)
                                       + " AD: " + str(adusr_attr_val) + ". "
                                       + "Setting AD attribute to DS value.")
                    self._adam.setAttribute(linkid, itm.mappedAttribute,
                                            str(ds_attr_val))

    def _getUserName(self, dsusr: dict) -> str:
        """
        Given a row of data from the datasource, get a unique username for
        this user.
        """
        linkid = dsusr[DS_ACCOUNT_IDENTIFIER]
        if AD_SHOULD_GENERATE_USERNAME:
            # find a username creation rule that matches this user
            for itm in USERNAME_ASSIGNMENTS:
                if itm.match(dsusr):
                    method = itm
                    break
            if method is None:
                raise Exception(linkid + ": Could not find an appropriate"
                                     + " method for generating a username.")
            # Now we need to generate usernames and test them against AD until
            # a unique one is found..
            un = None
            for format in method.formats:
                undata = tuple([dsusr[fld] for fld in method.userNameFields])
                try:
                    un = method.getUserName(format, undata, AD_USERNAME_INVALID_CHARS)
                except UserNameInvalidFieldDataException as e:
                    raise e
                if not self._adam.getUserInfo("sAMAccountName", un):
                    break
                else:
                    un = None
            if un is None:  # None of the formats generated a unique un
                raise NoFreeUserNamesException(linkid + ": A username could not be generated "
                                "that was not already in use... ")
        else:
            # we presume that the data source is providing the username
            un = dsusr[DS_USERNAME_COLUMN_NAME]
        return un

    def _getPasswordAssignment(self, dsusr: dict) -> PasswordAssignment:
        """
        Looks for a password generation method that this user matches
        and returns it (or None if not found).
        """
        # Locate a password assignment that matches this user's attributes.
        passwd = None
        for itm in PASSWORD_ASSIGNMENTS:
            if itm.match(dsusr):
                passwd = itm
        return passwd

    def _createUser(self, dsusr: dict) -> str:
        """
        Creates an AD user with the provided row of user information
        (dict, form { column: data }) from the datasource.
        Returns the UPN of the new user
        """
        linkid = dsusr[DS_ACCOUNT_IDENTIFIER]

        # Grab the username (samaccountname/cn for the new user)
        un = str(self._getUserName(dsusr))

        # Generate the upn from the un and the base user dn
        if bool(re.match("DC=", AD_BASE_USER_DN, flags=re.I)):
            upnsuffix = AD_BASE_USER_DN
        else:
            upnsuffix = ".".join(re.split(",DC=",
                                          AD_BASE_USER_DN,
                                          flags=re.I)[1:])
        upn = un + "@" + upnsuffix
        self._logger.debug(linkid + ": UPN will be " + upn)

        destination_ou = None
        for ou in AD_OU_ASSIGNMENTS:
            if ou.match(dsusr):
                self._logger.debug(linkid + ": Matching org unit found: "
                                   + ou.orgUnitDN)
                destination_ou = ou.orgUnitDN
                break
        if destination_ou is None:
            # It appears there were no OU matches for this user.  Set their OU to
            # the default OU specified in settings.
            destination_ou = AD_DEFAULT_USER_OU
            self._logger.debug(linkid + ": No OU assignments found. Assigning "
                               + "new user to " + "default OU.")
        # Create the user
        self._adam.createUser(linkid, un, destination_ou, un, upn)
        return upn
