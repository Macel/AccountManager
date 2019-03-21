"""
Author: Robert Meany
Updated: 3/19/2019
Description: Defines the mapping of the data in a column from the data source
to the target attribute in the AccountManager's target database.
"""


class AttributeMapping():
    SYNCHRONIZED = True
    NOT_SYNCHRONIZED = False

    def __init__(self, sourceColumnName: str, mappedAttribute: str,
                 synchronized: bool = SYNCHRONIZED):
        self._sourceColumnName = sourceColumnName
        self._mappedAttribute = mappedAttribute
        self._synchronized = synchronized

    @property
    def sourceColumnName(self) -> str:
        """
        Returns the name of the data source column for this mapping
        """
        return self._sourceColumnName

    @property
    def mappedAttribute(self) -> str:
        """
        Returns the name of the mapped attribute in the target db for this
        mapping.
        """
        return self._mappedAttribute

    @property
    def synchronized(self) -> bool:
        """
        Returns true if this attribute is meant to be kept synchronized after
        initial account creation in the target database.
        """
        return self._synchronized
