"""
Author: Robert Meany
Modified: 3/19/2019
Description: Active Directory-specific implementation of AccountManager that
handles all sync operations for an AD domain.
"""

from AccountManager import AccountManager
from pyad import pyad
from pyad import pyad_setdefaults
from AccountManager_Module_AD.ADOrgUnitAssignments import ADOrgUnitAssignment
from AssignmentRules import AssignmentRule
from AttributeMapping import AttributeMapping
from AccountManager_Module_AD.ADGroupAssignments import ADGroupAssignment


class ADAccountManager(AccountManager):
    AD_USERNAME_INVALID_CHARS = "/\\[]:;|=+*?<>\"@"

    def __init__(self, ldap_server: str, username: str, password: str,
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

        pyad_setdefaults(ldap_server=ldap_server, username=username,
                         password=password)
        self._orgUnitAssignments: ADOrgUnitAssignment = tuple(orgUnitAssignments)
        self._groupAssignments: ADGroupAssignment = tuple(securityGroupAssignments)

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
                                    ADAccountManager.AD_USERNAME_INVALID_CHARS)

    def performSync(self):
        """
        TODO: With the provided dataset, synchronizes account information to AD
        """
        # usr = pyad.aduser.ADUser.from_cn("Robert Meany")

        for usr in self._data:
            # print(usr[self.dataColumns("ID")])
            pass
