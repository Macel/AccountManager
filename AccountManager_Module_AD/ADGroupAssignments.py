from AssignmentRules import AssignmentRule


class ADGroupAssignment():
    MATCH_ANY_RULE = 0
    MATCH_ALL_RULES = 1
    SYNCHRONIZED = True
    NOT_SYNCHRONIZED = False

    def __init__(self, groupDN: str, synchronized: bool, matchMethod: int,
                 rules: AssignmentRule):
        self._groupDN = groupDN
        self._synchronized = synchronized
        self._matchMethod = matchMethod
        self._rules = rules

    @property
    def groupDN(self) -> str:
        """
        Returns the distinguished name of the group for this assignment.
        """
        return self._groupDN

    @property
    def synchronized(self) -> bool:
        """
        Returns true if this group assignment should be kept in sync after
        user account creation (if on the next update, they no longer match
        the rules, they will be removed from the AD secruity group.)
        """
        return self._synchronized

    @property
    def matchMethod(self) -> int:
        """
        Returns MATCH_ANY_RULE if the user qualifies for membership in this
        group if they match any one or more rule in the rules list.  Returns
        MATCH_ALL_RULES if the user must match all of the rules in order to
        qualify for membership in the group.
        """
        return self._matchMethod

    @property
    def rules(self) -> AssignmentRule:
        """
        Returns the list of ADGroupAssignmentRule objects that describe them
        requirements for user membership in this group assignment.
        """
        return self._rules

    def match(self, row: dict) -> bool:
        """
        Determines if the provided user information (as a dictionary of the
        form <fieldname: data>) matches the rules for membership in this Group.

        Looks at whether or not all rules must be a match or if any rule match
        qualifies for membership and returns true if the user should be
        assigned to this Group.
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
        rules in this ADGroupAssignment's AssignmentRules.

        Returns the number of rules that matched.
        """

        matchCount = 0
        for rule in self._rules:
            if rule.match(row[rule.sourceColumnName]):
                matchCount += 1
        return matchCount
