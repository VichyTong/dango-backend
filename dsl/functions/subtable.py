from dsl.functions import DangoFunction


class DangoSubtable(DangoFunction):
    def __init__(self):
        super().__init__(function_type="table")

    def definition(self):
        return """\
subtable(table, row_list=None, column_list=None): Returns a subtable with only the specified rows or columns.
Parameters:
- table (DataFrame, required): The table to extract the rows or columns from.
- row_list (list[int], optional): The list of row indices to be extracted.
- column_list (list[str], optional): The list of column names to be extracted.
Output:
- A pandas DataFrame.\
"""
