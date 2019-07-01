import logging
import logging.handlers
import re
from BufferingSMTPHandler import BufferingSMTPHandler
from Settings import \
    IMPORT_CHUNK_SIZE, DS_COLUMN_DEFINITION, \
    DS_ACCOUNT_IDENTIFIER, DS_STATUS_ACTIVE_VALUES, \
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
    RESET_PASS_COLUMN_NAME, AD_PASS_RESET_NOTIFICATION_SUBJECT, \
    AD_PASS_RESET_NOTIFICATION_MSG, ACCOUNT_NOTIFICATION_FIELDS


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
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Define any characters that should be excluded from newly generated usernames
# for AD.
AD_USERNAME_INVALID_CHARS = "/\\[]:;|=+*?<>\"@. "


class ADSyncer():
    # TODO: Make this an implementation of abstract class, AccountSyncer
    def __init__(self, logger: logging.Logger, args):
        self._logger = logger
        self._args = args

    def runSyncProcess(self):
        """
        Initiates the sync process.
        References the common and AD-related settings in Settings.py
        """
        if self._args.DatasourceFileType == 'TSV':
            dsfiletype = CSVPager.FILE_TYPE_TSV
        else:
            dsfiletype = CSVPager.FILE_TYPE_CSV

        # Sync accounts on paged data.
        pager = CSVPager(self._args.DatasourcePath,
                         dsfiletype,
                         IMPORT_CHUNK_SIZE,
                         DS_COLUMN_DEFINITION.get(DS_ACCOUNT_IDENTIFIER))
        self._logger.debug("pager total record count: " + str(pager.csvRecordCount))
        i = 0
        notify_emails = {}
        pass_reset_notify_emails = {}
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
                    try:
                        adusr = self._adam.getLinkedUserInfo(linkid,
                                                             *[atr.mappedAttribute
                                                              for atr in AD_ATTRIBUTE_MAP], "userPrincipalName")
                    except Exception as e:
                        self._logger.error(linkid + " An error occurred while attempting to query AD for "
                                           "linked user information.  Error details: " + str(e))
                        continue
                    # Are they linked to a user in AD (by their provided ID)?
                    if adusr is not None:  # If so,
                        # Sync any updated information
                        self._logger.debug("Linked user found for id: " + linkid
                                           + ".  Syncing information.")
                        # Verify that the user account has a valid UPN before continuing..
                        if not adusr['userPrincipalName'] is None:
                            upn = adusr['userPrincipalName'][0]
                        else:
                            self._logger.error(
                                linkid + ": Found a user in AD with no userPrincipalName"
                                " (upn) set. Cannot continue to sync information for this user until this"
                                " is addressed.  Will attempt again on the next scheduled sync."
                            )
                            continue
                        # Don't bother syncing attributes/group membership if
                        # the user is not active.
                        if (dsusr[DS_STATUS_COLUMN_NAME] in set(DS_STATUS_ACTIVE_VALUES)):
                            self._logger.debug(linkid + " is active, syncing attributes"
                                               + " and group membership.")
                            try:
                                self._syncAttributes(dsusr, adusr)
                            except Exception as e:
                                self._logger.error(linkid + "An error occurred while attempting to "
                                                   "sync attributes for this user.  Error details: "
                                                   + str(e))
                            try:
                                #if (linkid == 't4702'):
                                #    print("t4702")
                                self._syncGroupMembership(dsusr, adusr)
                            except Exception as e:
                                self._logger.error(linkid + "An error occurred while attempting to "
                                                   "sync group membership for this user.  Error details: "
                                                   + str(e))
                        else:
                            self._logger.debug(linkid + " is not active, will not bother"
                                               + " syncing attributes/group membership.")

                        # Check to see if a password reset is required and do so if necessary.
                        r = None
                        passwd = None
                        forcepwdchg = None
                        if dsusr[RESET_PASS_COLUMN_NAME] == "1":
                            if AD_SHOULD_GENERATE_PASSWORD:
                                try:
                                    r = self._genPassword(dsusr)
                                    passwd = r[0]
                                    forcepwdchg = r[1]
                                except Exception as e:
                                    self._logger.error(linkid + ": There was a problem generating the password for this user. "
                                                       "The password cannot be reset for this user until the problem is resolved.  "
                                                       "Error details: " + str(e))
                            else:
                                try:
                                    passwd = dsusr[DS_PASSWORD_COLUMN_NAME]
                                    forcepwdchg = True
                                except Exception:
                                    self._logger.error(linkid + ": The datasource does not appear to have a password column, but "
                                                       + "AD_SHOULD_GENERATE_PASSWORD is not set.  Cannot reset user password until "
                                                       + "this is resolved.")
                            if passwd:
                                try:
                                    self._adam.setUserPassword(linkid, passwd)
                                    # If this user has a notification assignment, add the notification to the password update notifications list.
                                    for notification in NEW_USER_NOTIFICATIONS:
                                        if notification.match(dsusr):
                                            updated_account_info = ["AD",upn,passwd] + \
                                                [self._adam.dataRow(linkid)[col]
                                                for col in ACCOUNT_NOTIFICATION_FIELDS]
                                            if notification.contacts in pass_reset_notify_emails:
                                                pass_reset_notify_emails[notification.contacts].append(updated_account_info)
                                            else:
                                                pass_reset_notify_emails[notification.contacts] = [updated_account_info]
                                    self._logger.info(linkid + ": The user's password has been reset.  upn: " + upn + ", Initial Password: " + passwd)
                                except Exception as e:
                                    # A problem occurred setting the password.
                                    self._logger.error(linkid + ": Attempting to reset password for existing user failed. "
                                                       "Error details: " + str(e))

                        # Sync active status *after* password reset
                        self._logger.debug(linkid + ": Syncing active status.")
                        try:
                            self._syncActiveStatus(dsusr, adusr)
                        except Exception as e:
                            self._logger.error(linkid + ": An error occurred while attempting to "
                                               "sync active status for this user.  Error details: "
                                               + str(e))

                        # Sync the OU last because if a user's OU changes,
                        # the OU information in adusr will become invalid.
                        self._logger.debug(linkid + ": Syncing OU.")
                        try:
                            self._syncOU(dsusr, adusr)
                        except Exception as e:
                            self._logger.error(linkid + ": An error occurred while attempting to "
                                               "sync the OU for this user.  Error details: "
                                               + str(e))
                    else:  # Linked user not found...
                        # Is the user active?
                        if (dsusr[DS_STATUS_COLUMN_NAME] in set(DS_STATUS_ACTIVE_VALUES)):
                            # See if a user exists with a match in the secondary field.
                            if (dsusr[DS_SECONDARY_MATCH_COLUMN] is not None
                                and len(dsusr[DS_SECONDARY_MATCH_COLUMN])) > 0:
                                # Don't match on an empty secondary field.
                                try:
                                    adusr = self._adam.getUserInfo(AD_SECONDARY_MATCH_ATTRIBUTE,
                                                                   dsusr[DS_SECONDARY_MATCH_COLUMN],
                                                                   AD_TARGET_ACCOUNT_IDENTIFIER,
                                                                   *[atr.mappedAttribute
                                                                     for atr in AD_ATTRIBUTE_MAP])
                                except Exception as e:
                                    self._logger.error(linkid + ": An error occurred while attempting to query AD for "
                                                       "information on this linked user. "
                                                       "Error details: " + str(e))
                                    continue
                            else:
                                adusr = None
                            if adusr is not None:
                                # Secondary match found,
                                # link the user by updating their ID in AD
                                # Sync any updated information

                                # First verify that the found user is not already
                                # linked to someone else in pschool..
                                if adusr['powerschoolID'] is not None:
                                    self._logger.warn(
                                        linkid + ": An AD account with a secondary "
                                        "field match was found for this unlinked user, but "
                                        "it appears to already be linked to another user.  "
                                        "Since secondary match attributes must be unique, "
                                        "this user cannot be linked until this issue is resolved. "
                                        "The datasource may be providing a duplicate user. "
                                        "The conflicting account in AD is: "
                                        + adusr['distinguishedName'][0]
                                    )
                                    continue

                                self._logger.debug(linkid + ": Secondary match found for '"
                                                   + AD_SECONDARY_MATCH_ATTRIBUTE
                                                   + "'': " + dsusr[DS_SECONDARY_MATCH_COLUMN]
                                                   + ".  Linking the user."
                                                   + "  Their account information will be synchronized"
                                                   + " on the next sync process run.")
                                try:
                                    self._adam.linkUser(dsusr[DS_SECONDARY_MATCH_COLUMN],
                                                        linkid)
                                except Exception as e:
                                    self._logger.error(linkid + ": An error occurred while attempting to link an "
                                                       "existing AD user to the datasource. "
                                                       " Error details: " + str(e))
                                    continue
                                self._logger.info(linkid + ": An unlinked AD user has been found with"
                                                  + " a matching secondary attribute and linked."
                                                  + " the rest of their information will be synced"
                                                  + " during the next sync process run.")
                            else:
                                # No secondary match found,
                                # Create the user
                                # Grab password for new user and set the
                                # forcepwdchg flag accordingly
                                if AD_SHOULD_GENERATE_PASSWORD:
                                    try:
                                        r = self._genPassword(dsusr)
                                    except Exception as e:
                                        self._logger.error(linkid + ": There was a problem generating the password for this user. "
                                                           "The user will not be created until the problem is resolved.  "
                                                           "Error details: " + str(e))
                                        continue
                                    passwd = r[0]
                                    forcepwdchg = r[1]
                                else:
                                    try:
                                        passwd = dsusr[DS_PASSWORD_COLUMN_NAME]
                                        forcepwdchg = True
                                    except Exception:
                                        self._logger.error(linkid + ": The datasource does not appear to have a password column, but "
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
                                try:
                                    adusr = self._adam.getLinkedUserInfo(linkid,
                                                                        *[atr.mappedAttribute
                                                                        for atr in AD_ATTRIBUTE_MAP])
                                except Exception as e:
                                    self._logger.error(linkid + ": An error occurred while attempting to query AD for linked "
                                                       "user information on this newly created user. Error details: " + str(e))
                                    try:
                                        self._adam.deleteUser(linkid)
                                    except Exception as ex:
                                        self._logger.error(linkid + ": An error occurred while attempting to delete user "
                                                           "object after a failed creation attempt. This user may need to be "
                                                           "manually deleted in AD so creation can be attempted again. "
                                                           "Error details: " + str(ex))
                                    continue

                                # Set additional attributes for the user per
                                # the attribute map...
                                try:
                                    self._syncAttributes(dsusr, adusr)
                                except Exception as e:
                                    self._logger.error(linkid + ": An error occurred while syncing attributes "
                                                       "for this user.  Error details: " + str(e))
                                    try:
                                        self._adam.deleteUser(linkid)
                                    except Exception as ex:
                                        self._logger.error(linkid + ": An error occurred while attempting to delete user "
                                                           "object after a failed creation attempt. This user may need to be "
                                                           "manually deleted in AD so creation can be attempted again. "
                                                           "Error details: " + str(ex))
                                    continue

                                # Join the user to any groups
                                try:
                                    self._syncGroupMembership(dsusr, adusr, syncall=True)
                                except Exception as e:
                                    self._logger.error(linkid + ": An error occurred while syncing group membership "
                                                       "for this user.  Error details: " + str(e))
                                    try:
                                        self._adam.deleteUser(linkid)
                                    except Exception as ex:
                                        self._logger.error(linkid + ": An error occurred while attempting to delete user "
                                                           "object after a failed creation attempt. This user may need to be "
                                                           "manually deleted in AD so creation can be attempted again. "
                                                           "Error details: " + str(ex))
                                    continue
                                try:
                                    self._adam.setUserPassword(linkid, passwd)
                                except Exception as e:
                                    # A problem occurred setting the password.
                                    self._logger.error(linkid + ": Attempting to set password for new user failed. "
                                                       "Account will be deleted so password set can be attempted "
                                                       "again next time.  Error details: " + str(e))
                                    # Delete the user so creation will be re-attempted.
                                    try:
                                        self._adam.deleteUser(linkid)
                                    except Exception as ex:
                                        self._logger.error(linkid + ": Could not delete this user. Their account may need "
                                                          "to be manually deleted so creation can be attempted again."
                                                          "Error details: " + str(ex))
                                    continue
                                try:
                                    self._syncActiveStatus(dsusr, adusr)
                                except Exception as e:
                                    self._logger.error(linkid + ": An error occurred while attempting to activate the "
                                                       "new user account.  Error details: " + str(e))

                                # Force a password change if the flag is set.
                                if forcepwdchg:
                                    self._logger.debug(linkid + ": Will be forced to change password on next login")
                                    try:
                                        self._adam.forcePasswordChange(linkid)
                                    except Exception as e:
                                        self._logger.error(linkid + ": An error occurred while attempting to set the "
                                                           "\"User Must Change Password\" flag for this user. "
                                                           "The error details were: " + str(e))

                                self._logger.info(linkid + ": New account has been created.  upn: "
                                                  + upn + ", Initial password: " + passwd)
                                # Append the new user to a data structure which will be output to the accountinfo csv file
                                # (if this option is enabled)
                                #if self._args.AccountInfoExportPath:
                                #    output_data.append([datetime.datetime.now(), upn, passwd] + [self._adam.dataRow(linkid)[col]
                                #     for col in ACCOUNT_INFO_FILE_FIELDS])
                                # If this new user has a notification assignment, add the notification to the new user notifications list.
                                for notification in NEW_USER_NOTIFICATIONS:
                                    if notification.match(dsusr):
                                        new_account_info = ["AD",upn,passwd] + \
                                                    	   [self._adam.dataRow(linkid)[col]
                                                    		for col in ACCOUNT_NOTIFICATION_FIELDS]
                                        if notification.contacts in notify_emails:
                                            notify_emails[notification.contacts].append(new_account_info)
                                        else:
                                            notify_emails[notification.contacts] = [new_account_info]
                        else:
                            # Don't bother looking for a secondary match,
                            # or creating a new account,
                            # the user is not active to begin with...
                            # (for example, this could be a duplicate/old account)
                            self._logger.debug(
                                linkid + ": Unlinked user is not active, will not bother "
                                "looking for secondary match or creating a new account for this user."
                            )
            if i == -1:  # End of CSV file reached
                # Send out new user account notifications
                self._sendNewUserNotifications(notify_emails)
                self._sendPasswordResetNotifications(pass_reset_notify_emails)
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
            body = ("<p>" + AD_USER_NOTIFICATION_MSG + "</p><table>\n"
                "<tr>"
                "<td><b>TYPE</b></td>"
                "<td><b>USERNAME</b></td>"
                "<td><b>PASS</b></td>"
            )
            for col in ACCOUNT_NOTIFICATION_FIELDS:
                body += "<td><b>" + col + "</b></td>"
            body += "</tr>\n"
            for row in notifications[recpts]:
                body += "<tr>"
                for val in row:
                    body += "<td>" + val + "</td>"
                body += "</tr>\n"
            body += "</html>"
            msg = MIMEMultipart('alternative')
            msgbody = MIMEText(body, 'html')
            msg['From'] = SMTP_FROM_ADDRESS
            msg['To'] = recipients
            msg['Subject'] = subject
            msg.attach(msgbody)
            try:
                server = SMTP(SMTP_SERVER_IP, SMTP_SERVER_PORT)
                server.send_message(msg)
            except SMTPException as e:
                self._logger.error("A problem occurred while attempting to send out a password reset notification email. "
                                   + "Error details as follows: " + str(e))

    def _sendPasswordResetNotifications(self, notifications: dict):
        """
        Takes a dictionary of the form { email-addresses : < new user info string > }
        and sends notifications for each entry in the dictionary.
        """
        for recpts in notifications.keys():
            recipients = ",".join(map(str, recpts))
            subject = AD_PASS_RESET_NOTIFICATION_SUBJECT
            body = ("<p>" + AD_PASS_RESET_NOTIFICATION_MSG + "</p><table>\n"
                "<tr>"
                "<td><b>TYPE</b></td>"
                "<td><b>USERNAME</b></td>"
                "<td><b>PASS</b></td>"
            )
            for col in ACCOUNT_NOTIFICATION_FIELDS:
                body += "<td><b>" + col + "</b></td>"
            body += "</tr>\n"
            for row in notifications[recpts]:
                body += "<tr>"
                for val in row:
                    body += "<td>" + val + "</td>"
                body += "</tr>\n"
            body += "</html>"
            msg = MIMEMultipart('alternative')
            msgbody = MIMEText(body, 'html')
            msg['From'] = SMTP_FROM_ADDRESS
            msg['To'] = recipients
            msg['Subject'] = subject
            msg.attach(msgbody)
            try:
                server = SMTP(SMTP_SERVER_IP, SMTP_SERVER_PORT)
                server.send_message(msg)
            except SMTPException as e:
                self._logger.error("A problem occurred while attempting to send out a password reset notification email. "
                                   + "Error details as follows: " + str(e))

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
        result = self._adam.assignUserGroups(linkid, *matchedgrps)
        if len(result) > 0:
            self._logger.info(linkid + ": was added to the following group(s): "
                              + str(result))

        # Now verify that the user is not in any synchronized groups that
        # they do *not* match the rules for....
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

                if ds_attr_val == '':
                    ds_attr_val = None

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

    def _genPassword(self, dsusr: dict) -> (str, bool):
        """
        Returns a tuple containing the password and true/false indicating whether
        or not the password should be reset on first login
        """
        pa = self._getPasswordAssignment(dsusr)
        if pa is None:
            raise Exception("Could not find a matching password assignment "
                            "method for new user.")
        else:
            passwd = pa.getPass()
            return (passwd, pa.usermustreset)
