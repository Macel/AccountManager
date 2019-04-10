from AssignmentRules import AssignmentRule


class ADOrgUnitAssignment():
    MATCH_ANY_RULE = 0
    MATCH_ALL_RULES = 1

    def __init__(self, orgUnitDN: str, matchMethod: int,
                 rules: AssignmentRule):
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
        return self._matchMethod

    @property
    def rules(self) -> AssignmentRule:
        """
        Returns a tuple of all the AssignmentRules in this ADOrgUnitAssignment
        """
        return self._rules

    def match(self, row: dict) -> bool:
        """
        Determines if the provided user information (as a dictionary of the
        form <fieldname: data>) matches the rules for membership in this OU.

        Looks at whether or not all rules must be a match or if any rule match
        qualifies for membership and returns true if the user should be
        assigned to this OU.
        """
        if self._matchMethod == self.MATCH_ALL_RULES:
            if self._ruleMatchCount(row) == len(self._rules):
                return True
            else:
                return False
        else:
            if self._ruleMatchCount(row) > 0:
                return True
            else:
                return False

    def _ruleMatchCount(self, row: dict) -> int:
        """
        Takes a row of data (as a dictionary of the form <fieldname: data>)
        and checks to see if the data in the provided fields matches the regex
        rules in this ADOrgUnitAssignment's AssignmentRules.

        Returns the number of rules that matched.
        """

        matchCount = 0
        for rule in self._rules:
            if rule.match(row[rule.sourceColumnName]):
                matchCount += 1
        return matchCount
