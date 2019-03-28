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
import random


class AccountManager(ABC):
    PASS_TYPE_WORDS = 0
    PASS_TYPE_ALPHA = 1
    PASS_TYPE_ALPHA_NUMERIC = 2
    PASS_TYPE_ALPHA_SYMBOLS = 3

    def __init__(self, dataToImport: tuple, dataColumnHeaders: dict,
                 dataLinkColumnName: str, targetLinkAttribute: str,
                 attributesToMap: str = (), maxSize: int = 500):
        """
        dataToImport: A tuple containing records of data to import
        dataColumnHeaders: Names for the columns in dataToImport, in same order
        as data.
        dataLinkColumnName: The name of the column (as provided in
        dataColumnHeaders) that contains the unique identifier to link to the
        target database.
        targetLinkAttribute: The name of the attribute in the target database
        that will be linked to with the data in dataLinkColumnName.
        attributesToMap: a tuple of data source column -to- target attribute
        mappings.
        maxSize: as the maximum number of records this account
        manager will accept to work on.  If the import data set is larger than
        maxSize records, a seperate instance of AccountManager will need to be
        created.
        """
        super().__init__()
        self._data = dataToImport
        self._dataLinkColumnName = dataLinkColumnName
        self._targetLinkAttribute = targetLinkAttribute
        self._maxSize = maxSize
        self._attributeMappings = attributesToMap
        self._dataColumns = dataColumnHeaders

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

    def generateUserName(fields: str, format: str, excludeChars: str) -> str:
        """
        Specific implementations that inherit from AccountManager may wish
        to override this method and automatically apply the appropriate
        excludeChars.

        fields should be a tuple of strings that will comprise the username
        example: ("Robert","Meany","2015")

        format should be a tuple of strings representing the formatting codes
        to apply on each string in the tuple.
        example: ("LTR:3","LTR:50","RTL:2")

        "LTR:3" means to take up to the first 3 characters of the corresponding
        field in the username tuple.  If the corresponding field is shorter
        than 3 characters, the entire value of the first field will be included.

        "RTL:2" means to take the last two characters of the corresponding
        string in the username tuple. Again, if the corresponding string in the
        username tuple is 0 or 1 characters in length, the entire string will be
        included.

        The above example username and format tuples would form the username:
        RobMeany15
        """
        # Ensures if only one field / format code is sent, it is still iterable
        # in a tuple.
        if type(fields) is not tuple:
            fields = (fields,)
        if type(format) is not tuple:
            format = (format,)

        # Remove any characters that are specified as excluded from the username
        excludeChars = tuple(excludeChars)
        newfields = []
        for fld in fields:
            for char in excludeChars:
                fld = fld.replace(char, "")
            newfields.append(fld)
        fields = tuple(newfields,)
        newfields = None

        # fields = ("JeanPierre", "Gonzalez-Altimarano", "2015")
        # format = ("LTR:1", "LTR:12", "RTL:2")

        i = 0
        result = ""
        for itm in format:
            a = itm.split(":")
            if a[0] == "LTR":
                result += fields[i][:int(a[1])]
            elif a[0] == "RTL":
                result += fields[i][-int(a[1]):]
            i += 1
        return result

    def generatePassword(length: int, type: int,
                         firstwords: str = None,
                         secondwords: str = None) -> str:
        """
        Generate a password of the provided length and type.
        If the password type is AccountManager.PASS_TYPE_WORDS,
        the length is a minimum and the password may be equal to or
        longer than the length.  The password will be comprised of two
        random words and two numbers.

        If the password type is AccountManager.PASS_TYPE_ALPHA_SYMBOLS, a
        random string of upper and lower case letters, numbers and symbols,
        of the exact length provided will be created.

        If the password type is AccountManager.PASS_TYPE_ALPHA_NUMERIC,
        a random string of upper and lower case letters and numbers of the
        provided length will be created.

        If the password type is AccountManager.PASS_TYPE_ALPHA, a random
        string of upper and lower case letters of the provided length will
        be created.

        """
        passchars = ""

        if type == AccountManager.PASS_TYPE_WORDS:
            if firstwords is None or secondwords is None:
                raise LookupError("Must provide password lists if using "
                                  "PASS_TYPE_WORDS")
            pw = ""
            while len(pw) < length:
                pw = "" + random.choice(firstwords) \
                        + random.choice(secondwords) \
                        + str(random.randrange(10, 99))
        else:
            if type == AccountManager.PASS_TYPE_ALPHA:
                passchars = "abcdefghijklmnopqrstuvwxyz" \
                            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            elif type == AccountManager.PASS_TYPE_ALPHA_NUMERIC:
                passchars = "abcdefghijklmnopqrstuvwxyz" \
                            "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                            "1234567890"
            elif type == AccountManager.PASS_TYPE_ALPHA_SYMBOLS:
                passchars = "abcdefghijklmnopqrstuvwxyz" \
                            "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                            "1234567890" \
                            "!@#$%^&*():;,.?/\\-=+\""
            pw = "".join(random.sample(passchars, length))

        return pw
