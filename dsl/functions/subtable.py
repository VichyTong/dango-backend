from dsl.functions import DangoFunction


class DangoSubtable(DangoFunction):
    def __init__(self):
        super().__init__(function_type="table")

    def definition(self):
        return """\
subtable(table, rows=None, columns=None): Extracts a subtable from a DataFrame based on specified rows and/or columns.
Parameters:
- table (DataFrame, required): The table to extract the rows or columns from.
- rows (list[int/str], optional): A list of row labels or indices to be extracted. If None, all rows are included. Defaults to None.
- columns (list[str], optional): A list of column labels to be extracted. If None, all columns are included. Defaults to None.
Output:
- A pandas DataFrame.\
"""
