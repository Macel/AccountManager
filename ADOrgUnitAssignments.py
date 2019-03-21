class ADOrgUnitAssignmentRule():
    def __init__(self, sourceColumnName: str,
                 sourceColumnExpectedValueRegex: str):
        """
        sourceColumnName is the name of data source column to be checked
        sourceColumnExpectedValueRegex is a regular expression to test for
        matching values in the source column on each user.
        """
        self._sourceColumnName
        self._sourceColumnExpectedValueRegex


class ADOrgUnitAssignment():
    MATCH_ANY_RULE = 0
    MATCH_ALL_RULES = 1

    def __init__(self, orgUnitDN: str, matchMethod: int,
                 *rules: ADOrgUnitAssignmentRule):
        """
        orgUnitDN: The distringuished name of the OU that matching users
        should be placed in.
        matchMethod: 0 or 1, representing MATCH_ANY_RULE and
        MATCH_ALL_RULES respectively.  Determines whether all rules in this
        assignment need to be met in order to match this OU assignment, or just
        one of them.
        rules: One or more ADOrgUnitAssignmentRule objects
        that define a column in the data source and a regular expression string
        that values in that column need to match to match this org unit
        assignment.
        """
        self._rules = rules
        self._orgUnitDN = orgUnitDN

    @property
    def rules(self) -> tuple:
        """
        Returns a tuple of all the rules in this ADOrgUnitAssignment
        """
        return self._rules

    @property
    def orgUnitDN(self) -> str:
        """
        Returns the org unit distinguished name for this ADOrgUnitAssignment
        """
        return self._orgUnitDN
