"""
Author: Robert Meany
Modified: 3/19/2019
Description: Active Directory-specific implementation of AccountManager that
handles all sync operations for an AD domain.
"""

from AccountManager import AccountManager
from pyad import pyad
from pyad import adquery
from pyad import pyad_setdefaults
from AccountManager_Module_AD.ADOrgUnitAssignments import ADOrgUnitAssignment
from AssignmentRules import AssignmentRule
from AttributeMapping import AttributeMapping
from AccountManager_Module_AD.ADGroupAssignments import ADGroupAssignment
import ldap

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
        self._orgUnitAssignments = orgUnitAssignments
        self._attributesToMap = attributesToMap
        self._securityGroupAssignments = securityGroupAssignments
        self._maxSize = maxSize

    def __enter__(self):
        class ADAccountManager(AccountManager):
            def __init__(self, ldap_server: str, username: str, password: str,
                         baseUserDN: str,
                         dataToImport: tuple,
                         dataColumnHeaders: dict,
                         orgUnitAssignments: ADOrgUnitAssignment = (),
                         attributesToMap: AttributeMapping = (),
                         securityGroupAssignments: ADGroupAssignment = (),
                         maxSize: int = 500):
                """
                Takes the provided connection settings, a tuple of org unit assignment
                rules, an attribute map and a tuple of security group assignment rules
                """
                super().__init__(dataToImport, dataColumnHeaders, attributesToMap,
                                 maxSize)

                #pyad_setdefaults(ldap_server=ldap_server, username=username,
                #                 password=password)
                self._orgUnitAssignments: ADOrgUnitAssignment = tuple(orgUnitAssignments)
                self._groupAssignments: ADGroupAssignment = tuple(securityGroupAssignments)

                #TODO: Make SSL optional / specify require cert
                ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
                self._ld = ldap.initialize("ldaps://" + ldap_server)
                self._ld.set_option(ldap.OPT_REFERRALS, 0)
                self._ld.simple_bind_s(username, password)

                # Grab all users under the specified base OU

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
                                     self._orgUnitAssignments,
                                     self._attributesToMap,
                                     self._securityGroupAssignments,
                                     self._maxSize)
        return self.adam

    def __exit__(self, exc_type, exc_value, traceback):
        self.adam.finalize()  # close LDAP connection
