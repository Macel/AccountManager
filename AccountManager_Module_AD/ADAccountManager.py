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

AD_USERNAME_INVALID_CHARS = "/\\[]:;|=+*?<>\"@"


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
                 orgUnitAssignments: ADOrgUnitAssignment = (),
                 attributesToMap: AttributeMapping = (),
                 securityGroupAssignments: ADGroupAssignment = (),
                 maxSize: int = 500):
        self._ldap_server = ldap_server
        self._username = username
        self._password = password
        self._baseUserDN = baseUserDN
        self._dataToImport = dataToImport
        self._dataColumnHeaders = dataColumnHeaders
        self._dataLinkColumn = dataLinkColumnName
        self._targetLinkAttribute = targetLinkAttribute
        self._orgUnitAssignments = orgUnitAssignments
        self._attributesToMap = attributesToMap
        self._securityGroupAssignments = securityGroupAssignments
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
                         orgUnitAssignments: ADOrgUnitAssignment = (),
                         attributesToMap: AttributeMapping = (),
                         securityGroupAssignments: ADGroupAssignment = (),
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
                targetLinkAttribute: The name of the AD attribute
                """
                super().__init__(dataToImport, dataColumnHeaders,
                                 dataLinkColumnName, targetLinkAttribute,
                                 attributesToMap,
                                 maxSize)

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
                                  attributes: str) -> dict:
                """
                Returns a tuple of information pertaining to the user queried.
                Searches on the provided link identifying attribute
                (linkIDAttributeName) and value (linkID).
                Returns a dictionary of the attributes specified in the
                attributes parameter, or
                None if the linked user was not found.
                """
                # TODO: Make an abstractmethod for this in AccountManager
                search = "(" + self._targetLinkAttribute + "=" + str(linkID) + ")"
                r = self._ld.search(self._baseUserDN,
                                    ldap.SCOPE_SUBTREE,
                                    search,
                                    attributes)
                result_type, result_data = self._ld.result(r, 1)

                if len(result_data) == 0:
                    return None
                elif len(result_data) > 1:
                    raise Exception("Unexpected: More than one user was "
                                    + "returned from this unique ID search!")
                else:
                    return result_data[0][1]

            def locateUser(self, searchAttributeName: str,
                           searchAttributeValue: str) -> str:
                """
                Searches for a user based on the specified attribute and value
                returns the DN of any user(s) found in a tuple.
                """
                # TODO: Make an abstractmethod for this in AccountManager
                # TODO: Test
                n = ldap.filter.escape_filter_chars(searchAttributeName)
                v = ldap.filter.escape_filter_chars(searchAttributeValue)
                search = "(" + n + "=" + v + ")"
                r = self._ld.search(self._baseUserDN,
                                    ldap.SCOPE_SUBTREE,
                                    search,
                                    ["distinguishedName"])
                result_type, result_data = self._ld.result(r, 1)
                return result_data

            def generateUserName(fields: str, format: str):
                """
                Generate a username for active directory given the provided name fields
                from the data source and a format string explaining how many characters
                from each field and which order to use them in.  The ADAccountManager
                implementation of this function takes into consideration characters
                that are note valid in an AD username.
                fields should be a tuple of strings that will comprise the username
                example: ("Robert","Meany","2015")
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

                The above example username and format tuples would form the username:
                RobMeany15

                If the username strings contain any invalid AD characters, those
                characters will be removed *before* applying the formatting.
                """
                return AccountManager.generateUserName(fields, format,
                                                       AD_USERNAME_INVALID_CHARS)

            def finalize(self):
                # Close LDAP Connection
                self._ld.unbind()

        self.adam = ADAccountManager(self._ldap_server, self._username,
                                     self._password, self._baseUserDN,
                                     self._dataToImport,
                                     self._dataColumnHeaders,
                                     self._dataLinkColumn,
                                     self._targetLinkAttribute,
                                     self._orgUnitAssignments,
                                     self._attributesToMap,
                                     self._securityGroupAssignments,
                                     self._maxSize)
        return self.adam

    def __exit__(self, exc_type, exc_value, traceback):
        self.adam.finalize()  # close LDAP connection
