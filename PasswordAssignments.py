from AssignmentRules import AssignmentRule, MATCH_ALL_RULES, MATCH_ANY_RULE
import random

PASS_TYPE_WORDS = 0
PASS_TYPE_ALPHA = 1
PASS_TYPE_ALPHA_NUMERIC = 2
PASS_TYPE_ALPHA_SYMBOLS = 3
PASS_TYPE_STATIC = 4


class PasswordAssignment():

    def __init__(self, rules: AssignmentRule, matchMethod: int, length: int,
                 passtype: int, staticpass: str = None, firstwords: str = None,
                 secondwords: str = None, usermustreset: bool = True):
        """
        Creates a PasswordAssignment

        rules: a tuple of one or more AssignmentRules that define a regular
        expression that an attribute must match to qualify for this
        PasswordAssignment.

        matchMethod: MATCH_ALL_RULES if all rules specified in this assignment
        must be matched to qualify or MATCH_ANY_RULE if only one rule needs to
        be matched.

        length: The length of the generated password.

        type: one of PasswordAssignments.PASS_TYPE_WORDS, PASS_TYPE_ALPHA,
        PASS_TYPE_ALPHA_NUMERIC, PASS_TYPE_ALPHA_SYMBOLS or PASS_TYPE_STATIC
        defining what the password should be comprised of.

        If PASS_TYPE_WORDS is provided,
        firstwords and secondwords should also be provided as tuples of strings
        containing the words that should be used to build the password.

        IF PASS_TYPE_STATIC is provided, staticpass must contain the password
        to be assigned to the user account.  It is recommended to enforce a
        password reset on first login when using this option.

        usermustreset: If true, the user should be required to reset their
        password on the next login.

        Each tuple in formats should have the same number of formatting strings
        as the number of fields provided in userNameFields.
        """
        # pack into a 1-element tuple if only one value was provided.
        if type(rules) is not tuple:
            rules = (rules,)
        if type(firstwords) is not tuple:
            firstwords = (secondwords,)
        if type(secondwords) is not tuple:
            secondwords = (secondwords,)
        self._rules = rules
        self._firstwords = firstwords
        self._secondwords = secondwords
        self._matchMethod = matchMethod
        self._length = length
        self._passtype = passtype
        self._usermustreset = usermustreset

        if passtype == PASS_TYPE_STATIC:
            if staticpass is None:
                raise Exception("Must provide a static password if creating "
                                "a PasswordAssignment with PASS_TYPE_STATIC")
            self._staticpass = staticpass

    @property
    def matchMethod(self) -> int:
        """
        Returns MATCH_ANY_RULE if the user qualifies for this naming format
        if they match any one or more rule in the rules list.  Returns
        MATCH_ALL_RULES if the user must match all of the rules in order to
        qualify for this PasswordAssignment.
        """
        return self._matchMethod

    @property
    def rules(self) -> AssignmentRule:
        """
        Returns the list of AssignmentRule objects that describe the
        requirements for this password assignment.
        """
        return self._rules

    @property
    def firstwords(self) -> str:
        """
        Returns the tuple of first words that can be assigned as part of a word
        based password assignment.
        """
        return self._firstwords

    @property
    def secondwords(self) -> str:
        """
        Returns the tuple of second words that can be assigned as part of a word
        based password assignment.
        """
        return self._secondwords

    @property
    def length(self) -> int:
        """
        Returns the length requirement of this password assignment
        """
        return self._length

    @property
    def passtype(self) -> int:
        """
        Returns the password type (PASS_TYPE_ALPHA, PASS_TYPE_WORDS,
        PASS_TYPE_ALPHA_NUMERIC, PASS_TYPE_ALPHA_SYMBOLS)
        of this password assignment.
        """
        return self._passtype

    @property
    def usermustreset(self) -> bool:
        """
        Returns whether passwords generated from this assignment will require
        the user to reset on first login or not.
        """
        return self._usermustreset

    def match(self, row: dict) -> bool:
        """
        Returns true if the provided user is a match for this
        assignment's rules.
        """
        if self._matchMethod == MATCH_ANY_RULE:
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
        rules in this PasswordAssignment's AssignmentRules.

        Returns the number of rules that matched.
        """

        matchCount = 0
        for rule in self._rules:
            if rule.match(row[rule.sourceColumnName]):
                matchCount += 1
        return matchCount

    def getPass(self) -> str:
        """
        Generate a password using the parameters that defined this
        PasswordAssignment
        """
        passchars = ""

        if self._passtype == PASS_TYPE_WORDS:
            if self._firstwords is None or self._secondwords is None:
                raise LookupError("Must provide password lists if using "
                                  "PASS_TYPE_WORDS")
            pw = ""
            i = 0
            while len(pw) < self._length:
                pw = "" + random.choice(self._firstwords) \
                        + random.choice(self._secondwords) \
                        + str(random.randrange(10, 99))
                if i == 1000:
                    raise LookupError("Could not generate a long enough password "
                                      "with the given word lists in a reasonable "
                                      "amount of attempts.")
                i += 1
        elif self._passtype == PASS_TYPE_STATIC:
            # just return the static password
            pw = self._staticpass
        else:
            if self._passtype == PASS_TYPE_ALPHA:
                passchars = "abcdefghijklmnopqrstuvwxyz" \
                            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                while True:
                    pw = "".join(random.sample(passchars, self._length))
                    if self.verifyPasswordStrength(pw, PASS_TYPE_ALPHA):
                        break
            elif self._passtype == PASS_TYPE_ALPHA_NUMERIC:
                passchars = "abcdefghijklmnopqrstuvwxyz" \
                            "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                            "1234567890"
                while True:
                    pw = "".join(random.sample(passchars, self._length))
                    if self.verifyPasswordStrength(pw, PASS_TYPE_ALPHA_NUMERIC):
                        break
            elif self._passtype == PASS_TYPE_ALPHA_SYMBOLS:
                passchars = "abcdefghijklmnopqrstuvwxyz" \
                            "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                            "1234567890" \
                            "!@#$%^&*():;,.?/\\-=+\""
                while True:
                    pw = "".join(random.sample(passchars, self._length))
                    if self.verifyPasswordStrength(pw, PASS_TYPE_ALPHA_SYMBOLS):
                        break
        return pw

    def verifyPasswordStrength(self, pw: str, passtype: int) -> bool:
        """
        For the given passtype (PASS_TYPE_ALPHA, PASS_TYPE_ALPHA_NUMERIC,
        PASS_TYPE_ALPHA_SYMBOLS), verify that the password provided is "strong"
        (has at least one of each type of character for the given password type)
        Return true if so.
        """

        if passtype not in (PASS_TYPE_ALPHA,
                            PASS_TYPE_ALPHA_NUMERIC,
                            PASS_TYPE_ALPHA_SYMBOLS):
            raise Exception("Password type provided is not valid.")

        lowercount = 0
        uppercount = 0
        digitcount = 0
        specialcount = 0

        for letter in pw:
            if letter.islower():
                lowercount += 1
            elif letter.isupper():
                uppercount += 1
            elif letter.isdigit():
                digitcount += 1
            else:
                specialcount += 1

        if passtype == PASS_TYPE_ALPHA:
            if lowercount > 0 and uppercount > 0:
                return True
            else:
                return False
        elif passtype == PASS_TYPE_ALPHA_NUMERIC:
            if lowercount > 0 and uppercount > 0 and digitcount > 0:
                return True
            else:
                return False
        elif passtype == PASS_TYPE_ALPHA_SYMBOLS:
            if lowercount > 0 and uppercount > 0 and digitcount > 0 and specialcount > 0:
                return True
            else:
                return False
