from dsl.functions import DangoFunction


class DangoRearrange(DangoFunction):
    def __init__(self):
        super().__init__(function_type="column_row")

    def definition(self):
        return """\
rearrange(table, by_values, axis): Rearranges the rows or columns of the table based on the specified order.
Parameters:
- table (DataFrame, required): The table to rearrange.
- by_values (str or int, required): The row or column to use as the basis for rearranging the rows or columns.
- axis (str or int, required):
    - 0 or "index": Rearranges base on the values of a row.
    - 1 or "columns": Rearranges base on the values of a column.
Output:
- A pandas DataFrame.\
"""
