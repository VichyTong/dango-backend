from dsl.functions import DangoFunction


class DangoRearrange(DangoFunction):
    def __init__(self):
        super().__init__(function_type="column_row")

    def definition(self):
        return """\
rearrange(table_name, by_values=None, by_array=None, axis): Rearranges the rows or columns of the table based on the specified order.
Parameters:
- table_name (str, required): table to be rearranged.
- by_values (str, optional): If this parameter is set, the rows/columns will be rearranged based on the values in the specified row/column.
- by_array (str or list[str/int], optional): If this parameter is set, the rows/columns will be rearranged based on the order of the values in the array.
- axis (str or int, required):
    - 0 or "index": Indicates to rearrange rows. Rows will be rearranged based on the values in the specified row/column or the order in the array.
    - 1 or "columns": Indicates to rearrange columns. Columns will be rearranged based on the values in the specified row/column or the order in the array.
Output:
- A new table with the rearranged rows/columns.\
"""
