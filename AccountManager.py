"""
Author: Robert Meany
Updated: 3/18/2019
Description: Abstract class with common methods/configuration for
account managers of different data sources to sync information to.  Should
contain data structures specifying lists of fields to pull from the source,
along with information such as whether the field should remain synchronized
after account creation and whether the field is the unique identifier or if it
can be used to search for existing unsynchronized accounts.
"""

from abc import ABC, abstractmethod, abstractproperty


class AccountManager(ABC):

    def __init__(self, attributesToMap: tuple = (), maxSize: int = 500):
        """
        maxSize is defined as the maximum number of records this account
        manager will accept to work on.  If the import data set is larger than
        maxSize records, a seperate instance of AccountManager will need to be
        created.
        """
        super().__init__()
        self._data = []
        self._maxSize = maxSize
        self._attributeMappings = attributesToMap
        self._dataColumns = {}

    @abstractmethod
    def performSync(self):
        pass

    @property
    def dataColumns(self, columnName: str) -> int:
        """
        Returns the column number (zero-based index) of the requested column
        name or -1 if the column name does not exist.
        """
        return self._dataColumns.get(columnName, -1)

    @dataColumns.setter
    def dataColumns(self, columns: dict):
        """
        Sets the import data column mappings based on the provided dictionary
        expected format is { "Column Name" : <index> } where index is the zero
        based index of the data column assigned the column name in the import
        data list.
        """
        self._dataColumns = columns

    @property
    def attributeMappings(self) -> tuple:
        """
        Returns the list of mappings that match columns in the data source to
        attributes in the account manager's target database.
        """
        return self._attributeMappings

    @attributeMappings.setter
    def attributeMappings(self, mappings: tuple):
        """
        Sets the list of AttributeMapping objects that match columns in the
        data source to attributes in the account manager's target database.
        """
        self._attributeMappings = mappings

    @property
    def data(self) -> list:
        """
        Returns the data that this AccountManager will use to perform the sync
        process.
        """
        return self._data

    @data.setter
    def data(self, data: list):
        """
        importData is defined as a list of rows from an imported csv object
        that will be imported to the target database. Each item in the list is
        a list of strings containing the data columns.
        """

        if len(data) > self._maxSize:
            raise ValueError("The dataset record count exceeds the maximum "
                             "size this account manager can accept.")
        else:
            self._data = data
