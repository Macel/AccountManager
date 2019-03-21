"""
Author: Robert Meany
Updated: 3/18/2019
Description: Works with csv.reader to returns data paged in chunks
for handling large datasets.
"""

import csv


class CSVPager():
    FILE_TYPE_CSV = 'excel'
    FILE_TYPE_TSV = 'excel-tab'

    def __init__(self, filepath: str, filetype: str, pageSize: int):
        """
        filepath is the path to the file to iterate through for pagination
        filetype is a string representing the format of the data source file
        (use CSVPager.FILE_TYPE_CSV or .FILE_TYPE_TSV)
        pageSize is the number of records that should be returned per page.
        """
        try:
            self._file = open(filepath)
        except OSError:
            raise OSError("Error opening file at the provided path.")
            return None
        self._reader = csv.reader(self._file, filetype)
        self._pageSize: int = pageSize
        self._page: list = []

        # Get the CSV file record count without storing the whole thing in
        # memory
        i = 0
        for row in self._reader:
            i += 1
        self._csvRecordCount = i
        self._reset_reader()

    def _reset_reader(self):
        """
        Internal function that sets the reader cursor back to the beginning of
        the data source file.
        """
        self._file.seek(0, 0)

    def getPage(self, startIndex: int = 0) -> int:
        """
        Queries the next page, starting with the index provided.  If _pageSize
        additional records are found, stores them in the _page variable and
        returns the index of the last record returned + 1.
        If less than _pageSize records are returned before reaching EOF, return
        -1 to indicate we are done paging through the csv file.
        """

        i = 0
        p = []
        retval = -1
        pageEndIndex = startIndex + self._pageSize - 1

        for row in self._reader:
            if i >= startIndex:
                p.append(row)
            if i == self._csvRecordCount - 1:
                retval = -1
                break
            if i == pageEndIndex:
                retval = i + 1
                break
            i += 1
        self._page = p
        self._reset_reader()
        return retval

    @property
    def page(self) -> list:
        """
        Gets Current page of data or empty list if not set.
        """
        return self._page

    @property
    def csvRecordCount(self) -> int:
        """
        Return the record count on the this pager's CSV file.
        """
        return self._csvRecordCount
