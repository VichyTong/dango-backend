from dsl.functions import DangoFunction


class DangoRearrange(DangoFunction):
    def __init__(self):
        super().__init__(function_type="column_row")

    def definition(self):
        return """\
rearrange(table, by_values=None, by_array=None, axis): Rearranges the rows or columns of the table based on the specified order.
Parameters:
- table (DataFrame, required): The table to be rearranged.
- by_values (str, optional): If set, the rows or columns will be rearranged based on the values in the specified row or column.
- by_array (list[str/int], optional): If set, the rows or columns will be rearranged based on the order of the values in the array.
- axis (str or int, required):
    - 0 or "index": Indicates that rows will be rearranged based on the values in the specified row or column or the order in the array.
    - 1 or "columns": Indicates that columns will be rearranged based on the values in the specified row or column or the order in the array.
Output:
- A pandas DataFrame.\
"""
