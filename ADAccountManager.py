"""
Author: Robert Meany
Modified: 3/19/2019
Description: Active Directory-specific implementation of AccountManager that
handles all sync operations for an AD domain.
"""

from AccountManager import AccountManager
from pyad import pyad
from pyad import pyad_setdefaults
from ADOrgUnitAssignments import ADOrgUnitAssignment, ADOrgUnitAssignmentRule


class ADAccountManager(AccountManager):
    def __init__(self, ldap_server: str, username: str, password: str,
                 orgUnitAssignments: tuple = (),
                 attributesToMap: tuple = (),
                 securityGroupAssignments: tuple = (),
                 maxSize: int = 500):
        """
        Takes the provided connection settings, a tuple of org unit assignment
        rules, an attribute map and a tuple of security group assignment rules
        """
        super().__init__(maxSize, attributesToMap)

        pyad_setdefaults(ldap_server=ldap_server, username=username,
                         password=password)
        self._orgUnitAssignments = orgUnitAssignments
        self._securityGroupAssignments = ()

    def performSync(self) -> str:
        """
        TODO: With the provided dataset, synchronizes account information to AD
        """

        usr = pyad.aduser.ADUser.from_cn("Robert Meany")
        return str(usr.adsPath)
