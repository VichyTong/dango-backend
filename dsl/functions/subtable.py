from dsl.functions import DangoFunction


class DangoSubtable(DangoFunction):
    def __init__(self):
        super().__init__(function_type="table")

    def definition(self):
        return """\
subtable(table, row_list=None, column_list=None): Returns a subtable with only the specified rows or columns.
Parameters:
- table (DataFrame, required): The table to extract the rows or columns from.
- row_list (list[str], optional): The list of row labels to be extracted. If row_list is None, all rows are included.
- column_list (list[str], optional): The list of column labels to be extracted. If column_list is None, all columns are included.
Output:
- A pandas DataFrame.\
"""
