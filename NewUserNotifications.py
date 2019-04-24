from AssignmentRules import AssignmentRule


class NewUserNotification():
    MATCH_ANY_RULE = 0
    MATCH_ALL_RULES = 1

    def __init__(self, rules: AssignmentRule, matchMethod: int,
                 *contacts: str):
        """
        Sets up a new user notification which contains the set of rules that
        define who should receive the notification when a new user is created
        based on one or more attributes on the new user, the email address(es)
        that should be contacted and the message format.

        rules: a tuple of AssignmentRules that determine whether or not this
        notification applieS to the new account in question.

        matchMethod: MATCH_ANY_RULE if a match on any rule in the rules list
        qualifies this notification to be sent.  MATCH_ALL_RULES if all rules
        must match.

        contacts: one or more email addresses that the notification should be
        sent to.
        """
        self._rules = rules
        self._matchMethod = matchMethod
        self._contacts = contacts

    @property
    def rules(self):
        return self._rules

    @property
    def matchMethod(self):
        return self._matchMethod

    @property
    def contacts(self):
        return self._contacts

    def match(self, row: dict) -> bool:
        """
        Returns true if the provided datasource row is a match for this
        assignment's rules.
        """
        if self._matchMethod == self.MATCH_ANY_RULE:
            if self._ruleMatchCount(row) > 0:
                return True
            else:
                return False
        else:
            if self._ruleMatchCount(row) == len(self._rules):
                return True
            else:
                return False

    def _ruleMatchCount(self, row: dict) -> int:
        """
        Takes a row of data (as a dictionary of the form <fieldname: data>)
        and checks to see if the data in the provided fields matches the regex
        rules in this UserNameAssignment's AssignmentRules.

        Returns the number of rules that matched.
        """
        matchCount = 0
        for rule in self._rules:
            if rule.match(row[rule.sourceColumnName]):
                matchCount += 1
        return matchCount
