class AssignmentRule():
    def __init__(self, sourceColumnName: str,
                 sourceColumnExpectedValueRegex: str):
        """
        sourceColumnName is the name of data source column to be checked
        sourceColumnExpectedValueRegex is a regular expression to test for
        matching values in the source column on each user.
        """
        self._sourceColumnName = sourceColumnName
        self._sourceColumnExpectedValueRegex = sourceColumnExpectedValueRegex

    @property
    def sourceColumnName(self) -> str:
        """
        Returns the name of the column in the data source to test for this rule
        """
        return self._sourceColumnName

    @property
    def sourceColumnExpectedValueRegex(self) -> str:
        """
        Returns the regular expression of the value that the current user must
        match for the given column name in the current OU assignment rule.
        """
        return self._sourceColumnExpectedValueRegex
