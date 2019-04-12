"""
Author: Robert Meany
Modified: 3/19/2019
Description: Active Directory-specific implementation of AccountManager that
handles all sync operations for an AD domain.
"""

from AccountManager import AccountManager
from AccountManager_Module_AD.ADOrgUnitAssignments import ADOrgUnitAssignment
from AssignmentRules import AssignmentRule
from AttributeMapping import AttributeMapping
from AccountManager_Module_AD.ADGroupAssignments import ADGroupAssignment
import ldap
from ldap.controls import SimplePagedResultsControl
from ldap.modlist import addModlist, modifyModlist
from ldap.filter import escape_filter_chars

"""
Active Directory Attribute Constants Definitions
"""
AD_USERNAME_INVALID_CHARS = "/\\[]:;|=+*?<>\"@"
UAC_OBJECT_SCRIPT = 1
UAC_OBJECT_DISABLED = 2
UAC_OBJECT_HOMEDIR_REQUIRED = 8
UAC_OBJECT_LOCKOUT = 16
UAC_OBJECT_PASSWD_NOTREQD = 32


class GetADAccountManager():
    """
    Provider for ADAccountManager instances.  Used in 'with' clause, thereby
    enforcing the closing of the LDAP connection upon exit from 'with'.
    """

    def __init__(self, ldap_server: str, username: str, password: str,
                 baseUserDN: str,
                 dataToImport: tuple,
                 dataColumnHeaders: dict,
                 dataLinkColumnName: str,
                 targetLinkAttribute: str,
                 secondaryMatchAttribute: str,
                 orgUnitAssignments: ADOrgUnitAssignment = (),
                 attributesToMap: AttributeMapping = (),
                 securityGroupAssignments: ADGroupAssignment = (),
                 targetEncoding: str = "utf-8",
                 maxSize: int = 500):
        """
        Create an AD Account Manager with the provided information.
        Parameters:

        ldap_server: dns name or ip address of ldap server.

        username: username of service account to bind with.

        password: password of service account to bind with.

        baseUserDN: the search base in LDAP to base user searches on.

        dataToImport: A dict containing rows of user data to sync.
        the dict key should be the identifer that links the data source
        to the AD user attribute.

        dataColumnHeaders: A tuple containing the column headers for the
        provided data (in the same order as the data.)

        dataLinkColumnName: The name of the column (as provided in
        dataColumnHeaders) that is the identifier for linking user data
        in dataToImport to AD user accounts.

        targetLinkAttribute: The name of the AD attribute that holds
        the link ID.

        secondaryMatchAttribute: The name of the AD attribute that can be
        matched against to link a user if they are not already linked.  Should
        be an attribute that is guaranteed to be unique forest-wide.

        defaultOrgUnit: The org unit to which an account should be
        assigned if there is no matching rule for the account in
        orgUnitAssignments.

        orgUnitAssignments: a tuple of ADOrgUnitAssignments that define
        rules which determine which org unit a user should be a member
        of.

        attributesToMap: a tuple of AttributeMappings that will sync
        user information from the datasource to the target db.

        securityGroupAssignments: a tuple of ADGroupAssignments that
        defines rules which determine whether the user should or should
        not be a member of a security group in AD.

        targetEncoding: the character set encoding in use by this ldap
        provider.  AD uses utf-8 and this is the default for this value
        if not provided.

        maxSize: The maximum number of records this AccountManager will
        accept to operate on.
        """
        self._ldap_server = ldap_server
        self._username = username
        self._password = password
        self._baseUserDN = baseUserDN
        self._dataToImport = dataToImport
        self._dataColumnHeaders = dataColumnHeaders
        self._dataLinkColumn = dataLinkColumnName
        self._targetLinkAttribute = targetLinkAttribute
        self._secondaryMatchAttribute = secondaryMatchAttribute
        self._orgUnitAssignments = orgUnitAssignments
        self._attributesToMap = attributesToMap
        self._securityGroupAssignments = securityGroupAssignments
        self._targetEncoding = targetEncoding
        self._maxSize = maxSize

    def __enter__(self):
        class ADAccountManager(AccountManager):
            FIRST_AD_USERS_PAGE = b''

            def __init__(self, ldap_server: str, username: str, password: str,
                         baseUserDN: str,
                         dataToImport: dict,
                         dataColumnHeaders: dict,
                         dataLinkColumnName: str,
                         targetLinkAttribute: str,
                         secondaryMatchAttribute: str,
                         defaultOrgUnit: str,
                         orgUnitAssignments: ADOrgUnitAssignment = (),
                         attributesToMap: AttributeMapping = (),
                         securityGroupAssignments: ADGroupAssignment = (),
                         targetEncoding: str = "utf-8",
                         maxSize: int = 1000):
                """
                Create an AD Account Manager with the provided information.
                Parameters:

                ldap_server: dns name or ip address of ldap server.

                username: username of service account to bind with.

                password: password of service account to bind with.

                baseUserDN: the search base in LDAP to base user searches on.

                dataToImport: A dict containing rows of user data to sync.
                the dict key should be the identifer that links the data source
                to the AD user attribute.

                dataColumnHeaders: A tuple containing the column headers for the
                provided data (in the same order as the data.)

                dataLinkColumnName: The name of the column (as provided in
                dataColumnHeaders) that is the identifier for linking user data
                in dataToImport to AD user accounts.

                targetLinkAttribute: The name of the AD attribute that holds
                the link ID.

                defaultOrgUnit: The org unit to which an account should be
                assigned if there is no matching rule for the account in
                orgUnitAssignments.

                orgUnitAssignments: a tuple of ADOrgUnitAssignments that define
                rules which determine which org unit a user should be a member
                of.

                attributesToMap: a tuple of AttributeMappings that will sync
                user information from the datasource to the target db.

                securityGroupAssignments: a tuple of ADGroupAssignments that
                defines rules which determine whether the user should or should
                not be a member of a security group in AD.

                targetEncoding: the character set encoding in use by this ldap
                provider.  AD uses utf-8 and this is the default for this value
                if not provided.

                maxSize: The maximum number of records this AccountManager will
                accept to operate on.
                """
                super().__init__(dataToImport, dataColumnHeaders,
                                 dataLinkColumnName, targetLinkAttribute,
                                 secondaryMatchAttribute, attributesToMap,
                                 targetEncoding, maxSize)

                self._orgUnitAssignments: ADOrgUnitAssignment = tuple(orgUnitAssignments)
                self._groupAssignments: ADGroupAssignment = tuple(securityGroupAssignments)
                self._baseUserDN = baseUserDN

                # TODO: Make SSL optional / specify require cert
                ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
                self._ld = ldap.initialize("ldaps://" + ldap_server)
                self._ld.set_option(ldap.OPT_REFERRALS, 0)
                self._ld.simple_bind_s(username, password)

            def _pagedSearch(self, attributes: str, searchString: str = None,
                             pageSize: int = 1000, bookmark: str = ''):
                """
                searchString: The LDAP query

                attributes: the desired attributes returned from the query.

                pageSize: number of results this function should return.

                bookmark: if previous pages already returned, this is the
                bookmark for the next page.

                returns: a tuple containing a tuple attributes per user returned
                by the query and the bookmark for the next page.
                """
                pagecontrol = SimplePagedResultsControl(True,
                                                        size=self._maxSize,
                                                        cookie=bookmark)
                response = self._ld.search_ext(self._baseUserDN,
                                               ldap.SCOPE_SUBTREE,
                                               searchString,
                                               attributes,
                                               serverctrls=[pagecontrol])

                rtype, rdata, rmsgid, serverctrls = self._ld.result3(response)
                controls = [control for control in serverctrls
                            if control.controlType
                            == SimplePagedResultsControl.controlType]

                return (rdata, controls[0].cookie)

            def getADUsersPage(self, attributes, bookmark: bytes = ''):
                """
                Given a set of attributes to return and a bookmark representing
                the next page to retrieve, retrieve a page of AD users.
                The number of AD users returned (page size) is less than or
                equal to the maxSize paramater given when this ADAccountManager
                was created.  The base DN for the user search is the base DN
                that was provided when this ADAccountManager was created.

                If bookmark is b'', first page is assumed.

                This function returns a tuple containing the list of AD users
                and the bookmark value for the next page.
                If the returned bookmark value is None, this is also the last
                page.
                """
                # TODO: Rename this to GetLinkedUsersPage
                # TODO: Make an abstractmethod for this in AccountManager

                if bookmark is None:
                    raise EOFError("End of user search has been reached.")
                r = self._pagedSearch(attributes,
                                      "(&(objectCategory=person)(objectClass=user))",
                                      self._maxSize, bookmark)
                if r[1] == b'':
                    retbookmark = None
                else:
                    retbookmark = r[1]
                return (r[0], retbookmark)

            def getLinkedUserInfo(self, linkID: str,
                                  *attributes: str) -> dict:
                """
                Gets a user by linkID and returns the requested attributes, if found.
                Returns an empty dictionary if no user found.

                searchAttributeName: The name of the AD attribute to search on
                searchAttributeValue: The value to look for in the search attribute.
                attributes: 1 or more attributes that should be returned as a
                dictionary of the form {attribute name: value} if a matching
                user was found.  If attributes is None, just the DN of the discovered
                user will be returned.
                """
                # TODO: Make an abstractmethod for this in AccountManager
                # TODO: Error Handling
                return self.getUserInfo(self._targetLinkAttribute, linkID, *attributes)

            def _getObjAttributes(self, dn: str, attributes: str) -> dict:
                """
                Returns the requested attributes for the specified dn as
                a dictionary.
                """
                search = "(distinguishedName=" + dn + ")"

                r = self._ld.search(self._baseUserDN,
                                    ldap.SCOPE_SUBTREE,
                                    search,
                                    tuple(["distinguishedName"] + list(attributes)))
                result_type, result_data = self._ld.result(r, 1)
                if len(result_data) == 0:
                    return None
                elif len(result_data) > 1:
                    raise Exception("Unexpected: More than one object was "
                                    + "returned from this unique ID search!")
                else:
                    adobj: dict = result_data[0][1]
                    retval = {}
                    for attribute in adobj.keys():
                        retval[attribute] = [val.decode(self._targetEncoding)
                                             for val in adobj[attribute]]
                    return retval

            def getUserInfo(self, searchAttributeName: str,
                            searchAttributeValue: str, *attributes: str) -> dict:
                """
                Searches for a user and returns the requested attributes, if found.
                Returns an empty dictionary if no user found.

                searchAttributeName: The name of the AD attribute to search on
                searchAttributeValue: The value to look for in the search attribute.
                attributes: 1 or more attributes that should be returned as a
                dictionary of the form {attribute name: value} if a matching
                user was found.  If attributes is None, just the DN of the discovered
                user will be returned.
                """
                # TODO: Make an abstractmethod for this in AccountManager
                searchAttributeName = escape_filter_chars(searchAttributeName)
                searchAttributeValue = escape_filter_chars(searchAttributeValue)
                search = "(" + searchAttributeName + "=" + searchAttributeValue + ")"
                # TODO: Error Handling
                r = self._ld.search(self._baseUserDN,
                                    ldap.SCOPE_SUBTREE,
                                    search,
                                    tuple(["distinguishedName"] + list(attributes)))
                result_type, result_data = self._ld.result(r, 1)

                if len(result_data) == 0:
                    return None
                elif len(result_data) > 1:
                    raise Exception("Unexpected: More than one user was "
                                    + "returned from this unique ID search!")
                else:
                    adusr: dict = result_data[0][1]
                    retval = {}
                    # Convert result data from bytes to friendly strings
                    for attribute in adusr.keys():
                        retval[attribute] = [val.decode(self._targetEncoding)
                                             for val in adusr[attribute]]
                    # The ldap interface does not return an empty/null attribute
                    # in its result data.  We should find any non-returned
                    # attributes and return them as null here so key Errors
                    # do not get raised unexpectedly.
                    nullatrs = [atr for atr in attributes
                                if atr not in adusr.keys()]
                    for atr in nullatrs:
                        retval[atr] = None
                    return retval

            def generateUserName(format: str, fields: str):
                """
                Generate a username for active directory given the provided name fields
                from the data source and a format string explaining how many characters
                from each field and which order to use them in.  The ADAccountManager
                implementation of this function takes into consideration characters
                that are note valid in an AD username.

                format should be a tuple of strings representing the formatting codes
                to apply on each string in the tuple.
                example: ("LTR:3","LTR:50","RTL:2")
                "LTR:3" means to take up to the first 3 characters of the corresponding
                field in the username tuple.  If the corresponding field is shorter
                than 3 characters, the entire value of the first field will be included.
                "RTL:2" means to take the last two characters of the corresponding
                string in the username tuple. Again, if the corresponding string in the
                username tuple is 0 or 1 characters in length, the entire string will be
                included.

                fields should be a tuple of strings that will comprise the username
                example: ("Robert","Meany","2015")

                The above example username and format tuples would form the username:
                RobMeany15

                If the username strings contain any invalid AD characters, those
                characters will be removed *before* applying the formatting.
                """
                return AccountManager.generateUserName(format, fields,
                                                       AD_USERNAME_INVALID_CHARS)

            def setAttribute(self, linkid: str, attributeName: str,
                             attributeValue: str):
                """
                By distinguishedName, Updates an existing AD user's attribute
                with the value provided. NOTE: this will *replace* whatever is
                in the attribute with what is provided.

                dn: the distinguishedName of the user.

                attributeName: Name of the AD attribute to update.

                attributeValue: The new value for the AD attribute.
                """

                dn = self.getLinkedUserInfo(linkid)["distinguishedName"][0]
                modlist = [(ldap.MOD_REPLACE, attributeName,
                            [attributeValue.encode(self._targetEncoding)])]
                # TODO: Error Handling
                self._ld.modify_s(dn, modlist)

            def linkUser(self, secondaryMatchVal: str, linkid: str):
                """
                Links the the target database user with the datasource on
                the provided value.  References the defined secondaryMatchAttribute
                (when this object was instantiated) for the name of the attribute that
                should be searched to find the user to link.

                secondaryMatchVal: the value of the AD secondary match field.

                linkid: the id that should link the datasource record to the target user.
                """
                searchattr = escape_filter_chars(self._secondaryMatchAttribute)
                searchval = escape_filter_chars(secondaryMatchVal)
                linkattr = escape_filter_chars(self._targetLinkAttribute)
                linkid = escape_filter_chars(linkid)
                dn = self.getUserInfo(searchattr, searchval)["distinguishedName"][0]
                modlist = [(ldap.MOD_REPLACE, linkattr,
                            [linkid.encode(self._targetEncoding)])]
                # TODO: Error Handling
                self._ld.modify_s(dn, modlist)

            def createUser(self, linkid: str, cn: str, ou: str, sAMAccountName: str,
                           upn: str, attributes: dict):
                """
                Create a new AD user account and enable it.

                linkid: The unique ID that maps the datasource user to the target db.

                cn: common name for the new user.

                ou: org unit the new user should be placed in.

                samAccountName: the username for the new user

                upn: the userPrincipalName (username + @domainsuffix)

                attributes: dictionary of additional optional attribute names and
                values to be set.

                groups: tuple of DNs of groups this account should be made a member of.
                """
                # Build new dn from cn and ou
                dn = "cn=" + cn + "," + ou

                # Define the object class for a new user in AD
                objclass = ["Top", "Person", "OrganizationalPerson", "User"]

                modlist = [("distinguishedName", [dn.encode(self._targetEncoding)]),
                           ("userPrincipalName", [upn.encode(self._targetEncoding)]),
                           ("objectClass", [i.encode(self._targetEncoding) for i in objclass]),
                           ("sAMAccountName", [sAMAccountName.encode(self._targetEncoding)]),
                           (self._targetLinkAttribute, [linkid.encode(self._targetEncoding)])]

                # Append attributes to the mod list.
                for key in attributes.keys():
                    moditm = (key, [attributes[key].encode(self._targetEncoding)])
                    modlist.append(moditm)

                # Create the user.
                try:
                    self._ld.add_s(dn, modlist)
                except Exception as e:
                    raise e

            def setUserOU(self, linkid: str, ou: str) -> bool:
                """
                Move a user to a different OU
                linkid: the unique id that links the source user to the target.
                ou: the DN of the org unit to move the user to.

                Returns true if the user was moved, false if the user was
                already in the OU.

                Raises an exception if there was a problem moving the user.
                """
                dn = self.getLinkedUserInfo(linkid)["distinguishedName"][0]
                # If the user's current ou matches the target ou, don't bother
                splitdn = dn.split(",", 1)
                cn = splitdn[0]
                currentou = splitdn[1]
                if (currentou == ou):
                    return False
                try:
                    self._ld.rename_s(dn, cn, ou)
                except Exception as e:
                    raise e
                return True

            def assignUserGroups(self, linkid: str, *groups: str) -> tuple:
                """
                Add a user to AD groups by user linkid
                linkid: the unique id that links the source user to the target.
                groups: one or more Group DNs to add this user to.
                Ignores any provided groups that the user is already a member of.

                Returns a tuple of DNs for groups that the user was not in and
                has been added to.
                """
                adusr = self.getLinkedUserInfo(linkid, "memberOf")
                adgrps = adusr["memberOf"]
                dn = adusr["distinguishedName"][0]

                # don't bother trying to add user to group they are already
                # a member of.
                if adgrps is not None:
                    grps_to_assign = [grp for grp in groups if grp not in adgrps]
                else:
                    grps_to_assign = [grp for grp in groups]

                modlist = [(ldap.MOD_ADD, "member",
                            [dn.encode(self._targetEncoding)])]
                for grp in grps_to_assign:
                    # TODO: Error Handling
                    self._ld.modify_s(grp, modlist)
                return tuple(grps_to_assign)

            def deassignUserGroups(self, linkid: str, *groups: str) -> tuple:
                """
                Remove a user from AD groups by user linkid.
                Ignores any provided groups that the user is not currently
                a member of.
                linkid: the unique id that links the source user to the target.
                groups: one or more Group DNs to remove this user from.

                Returns a tuple of DNs for groups that the user was in and
                has been removed from.
                """

                adusr = self.getLinkedUserInfo(linkid, "memberOf")
                adgrps = adusr["memberOf"]
                dn = adusr["distinguishedName"][0]

                grps_to_remove = [grp for grp in groups if grp in adgrps]
                modlist = [(ldap.MOD_DELETE, "member",
                            [dn.encode(self._targetEncoding)])]
                for grp in grps_to_remove:
                    # TODO: Error Handling
                    self._ld.modify_s(grp, modlist)
                return tuple(grps_to_remove)

            def setUserEnabled(self, linkid: str, enabled: bool):
                """
                Enable or disable a user by linkid.
                linkid: the unique id that links the source user to the target.
                enabled: true if user should be enabled, false if user should be
                disabled.

                Returns True if a change was made to the status and False if
                the current status already matches the desired status.
                """
                # TODO: Implement this as an abstractmethod in AccountManager
                if (self.userEnabled(linkid) == enabled):
                    return False
                else:
                    usr = self.getLinkedUserInfo(linkid, "userAccountControl")
                    uacval = int(usr["userAccountControl"][0])
                    dn = usr["distinguishedName"][0]
                    if enabled:
                        modlist = [(ldap.MOD_REPLACE, "userAccountControl",
                                    [str(uacval - UAC_OBJECT_DISABLED)
                                    .encode(self._targetEncoding)])]
                    else:
                        modlist = [(ldap.MOD_REPLACE, "userAccountControl",
                                    [str(uacval + UAC_OBJECT_DISABLED)
                                    .encode(self._targetEncoding)])]
                    try:
                        self._ld.modify_s(dn, modlist)
                        return True
                    except Exception as e:
                        raise e

            def userEnabled(self, linkid) -> bool:
                """
                Returns true if the user is enabled or false if not.
                linkid: the unique id that links the source user to the target.
                """
                # TODO: Implement this as an abstractmethod in AccountManager
                usr = self.getLinkedUserInfo(linkid, ("userAccountControl"))
                uacval = int(usr["userAccountControl"][0])
                if ((uacval & UAC_OBJECT_DISABLED)
                    == UAC_OBJECT_DISABLED):
                    return False
                else:
                    return True

            def finalize(self):
                # Close LDAP Connection
                self._ld.unbind()

        self.adam = ADAccountManager(self._ldap_server, self._username,
                                     self._password, self._baseUserDN,
                                     self._dataToImport,
                                     self._dataColumnHeaders,
                                     self._dataLinkColumn,
                                     self._targetLinkAttribute,
                                     self._secondaryMatchAttribute,
                                     self._orgUnitAssignments,
                                     self._attributesToMap,
                                     securityGroupAssignments=self._securityGroupAssignments,
                                     targetEncoding=self._targetEncoding,
                                     maxSize=self._maxSize)
        return self.adam

    def __exit__(self, exc_type, exc_value, traceback):
        self.adam.finalize()  # close LDAP connection
