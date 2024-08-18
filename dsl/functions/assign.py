from dsl.functions import DangoFunction


class DangoAssign(DangoFunction):
    def __init__(self):
        super().__init__(function_type="column_row")

    def definition(self):
        return """\
assign(table_name, start_row_index, end_row_index, start_column_index, end_column_index, values): Assigns constant values to specific cells in the table.
Parameters:
- table_name (str, required): The name of the table to assign the value to.
- start_row_index, end_row_index (int, required): The range of row indices to assign the value to.
- start_column_index, end_column_index (int, required): The range of column indices to assign the value to.
- values (list[list[int/float/str]] or int/float/str, required): The const value(s) to assign to the specified cell(s). Can be a single int/float/str or a list of lists of int/float/str. The order of values is from top to bottom, left to right.
Output:
- A new table with the specified cells assigned with the specified values.\
"""
