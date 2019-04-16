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
from PasswordAssignments import PASS_TYPE_ALPHA, PASS_TYPE_ALPHA_NUMERIC, \
                                PASS_TYPE_ALPHA_SYMBOLS, PASS_TYPE_WORDS


class AccountManager(ABC):

    def __init__(self, dataToImport: dict, dataColumnHeaders: dict,
                 dataLinkColumnName: str, targetLinkAttribute: str,
                 secondaryMatchAttribute: str,
                 attributesToMap: str = (), targetEncoding: str = None,
                 maxSize: int = 500):
        """
        dataToImport: A dict containing records of data to import with
        the user identifier as the key.

        dataColumnHeaders: Names for the columns in dataToImport, in same order
        as data.

        dataLinkColumnName: The name of the column (as provided in
        dataColumnHeaders) that contains the unique identifier to link to the
        target database.

        targetLinkAttribute: The name of the attribute in the target database
        that will be linked to with the data in dataLinkColumnName.
        attributesToMap: a tuple of data source column -to- target attribute
        mappings.

        secondaryMatchAttribute: The name of the target DB attribute that can be
        matched against to link a user if they are not already linked.  Should
        be an attribute that is guaranteed to be unique in the target DB.

        maxSize: as the maximum number of records this account
        manager will accept to work on.  If the import data set is larger than
        maxSize records, a seperate instance of AccountManager will need to be
        created.
        """
        super().__init__()
        self._data = dataToImport
        self._dataLinkColumnName = dataLinkColumnName
        self._targetLinkAttribute = targetLinkAttribute
        self._secondaryMatchAttribute = secondaryMatchAttribute
        self._maxSize = maxSize
        self._attributeMappings = attributesToMap
        self._dataColumns = dataColumnHeaders
        self._targetEncoding = targetEncoding
        self._ds_col_linkid = self._dataColumns.get(dataLinkColumnName)

    def dataColumns(self, *columnName: str) -> int:
        """
        Returns the column number(s) (zero-based index) of the requested column
        name(s) or -1 if the column name does not exist.
        """

        result = [self._dataColumns.get(i, -1) for i in columnName]

        # if only one column is returned, do not encapsulate it in list.
        if len(result) == 1:
            result = result[0]
        return result

    @property
    def DS_COL_LINKID(self) -> int:
        """
        Returns the index of the column in this AccountManager's datasource
        that represents the linkid for the user accounts.
        """
        return self._ds_col_linkid

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
    def data(self) -> tuple:
        """
        Returns the data that this AccountManager will use to perform the sync
        process.
        """
        return self._data

    @data.setter
    def data(self, data):
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

    def dataRow(self, rowid) -> tuple:
        """
        Return a row of data with the provided record identifier key or None
        if the row identifier does not exist in the data.
        Row is returned as a dictionary of {"columnname": "value"}
        """
        result = {}
        datarow = self._data.get(rowid, [])
        for col in self._dataColumns.keys():
            result[col] = datarow[self._dataColumns[col]]
        return result

    @abstractmethod
    def linkUser(self, secondaryMatchVal: str, linkid: str):
        """
        Links the the target database user with the datasource on
        the provided value.  References the defined secondaryMatchAttribute
        (when this object was instantiated) for the name of the attribute that
        should be searched to find the user to link.

        secondaryMatchVal: the value of the target database secondary match field.

        linkid: the id that should link the datasource record to the target user.
        """
        pass

    @abstractmethod
    def setAttribute(self, userid, attributeName: str,
                     attributeValue: str):
        """
        Implementations of AccountManager should update linked user's target db
        attribute with the provided value.
        """
        pass

    @abstractmethod
    def createUser(self, userid):
        """
        Implementations of AccountManager should provide a method for creating
        new user accounts in the target database.
        """
        pass
