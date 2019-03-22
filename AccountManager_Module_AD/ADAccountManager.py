"""
Author: Robert Meany
Modified: 3/19/2019
Description: Active Directory-specific implementation of AccountManager that
handles all sync operations for an AD domain.
"""

from AccountManager import AccountManager
from pyad import pyad
from pyad import pyad_setdefaults
from ADOrgUnitAssignments import ADOrgUnitAssignment
from AssignmentRules import AssignmentRule
from AttributeMapping import AttributeMapping
from ADGroupAssignments import ADGroupAssignment


class ADAccountManager(AccountManager):
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

    def performSync(self) -> str:
        """
        TODO: With the provided dataset, synchronizes account information to AD
        """
        #usr = pyad.aduser.ADUser.from_cn("Robert Meany")

        # Test ADOrgUnitAssignments
        #for assignment in self._orgUnitAssignments:
        #    print("Org Unit DN: " + assignment.orgUnitDN)
        #    print("Match method: " + str(assignment.matchMethod))
        #    for rule in assignment.rules:
        #        print(rule.sourceColumnName + ": " + rule.sourceColumnExpectedValueRegex)

        # Test ADGroupAssignments
        #for assignment in self._groupAssignments:
        #    print("*****Group DN: " + assignment.groupDN)
        #    print("is synchronized: " + str(assignment.synchronized))
        #    print("match method: " + str(assignment.matchMethod))
        #    for rule in assignment.rules:
        #        print("rule: " + rule.sourceColumnName + ": " + rule.sourceColumnExpectedValueRegex)
        return ""
