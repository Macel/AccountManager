from AssignmentRules import AssignmentRule


class ADOrgUnitAssignment():
    MATCH_ANY_RULE = 0
    MATCH_ALL_RULES = 1

    def __init__(self, orgUnitDN: str, matchMethod: int,
                 *rules: AssignmentRule):
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
        self._matchMethod = matchMethod

    @property
    def orgUnitDN(self) -> str:
        """
        Returns the org unit distinguished name for this ADOrgUnitAssignment
        """
        return self._orgUnitDN

    @property
    def matchMethod(self) -> int:
        """
        Returns MATCH_ANY_RULE if the user qualifies for membership in this OU
        if they match any one or more AssignmentRules.  Otherwise returns
        MATCH_ALL_RULES if they must match all of the rules in this assignment.
        """
        return self._MatchMethod

    @property
    def rules(self) -> AssignmentRule:
        """
        Returns a tuple of all the AssignmentRules in this ADOrgUnitAssignment
        """
        return self._rules
