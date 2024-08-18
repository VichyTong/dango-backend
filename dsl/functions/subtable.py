from dsl.functions import DangoFunction


class DangoSubtable(DangoFunction):
    def __init__(self):
        super().__init__(function_type="table")

    def definition(self):
        return """\
subtable(table_name, row_list=None, column_list=None): Returns a new table with only the specified rows or columns.
Parameters:
- table_name (str, required): The name of the table to extract the rows/columns from.
- row_list (list[int], optional): The list of row indices to be extracted.
- column_list (list[str], optional): The list of column names to be extracted.
- subtable_name (str, optional): The name of the new table. If not provided, the new table will be named "subtable.csv".
Output:
- The new table with only the specified rows/columns.\
"""
