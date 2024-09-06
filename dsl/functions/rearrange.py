from dsl.functions import DangoFunction


class DangoRearrange(DangoFunction):
    def __init__(self):
        super().__init__(function_type="column_row")

    def definition(self):
        return """\
rearrange(table, by_values, axis): Rearranges the rows or columns of the table based on the specified order.
Parameters:
- table (DataFrame, required): The table to be rearranged.
- by_values (str, required): If set, the rows or columns will be rearranged based on the values in the specified row or column.
- axis (str or int, required):
    - 0 or "index": Indicates that rows will be rearranged based on the values in the specified row or column.
    - 1 or "columns": Indicates that columns will be rearranged based on the values in the specified row or column.
Output:
- A pandas DataFrame.\
"""
