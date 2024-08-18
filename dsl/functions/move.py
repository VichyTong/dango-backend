from dsl.functions import DangoFunction


class DangoMove(DangoFunction):
    def __init__(self):
        super().__init__(function_type="column_row")

    def definition(self):
        return """\
move(origin_table_name, origin_index, target_table_name, target_index, axis): Moves a row or column from the origin table to the target table.
Parameters:
- origin_table_name (str, required): The name of the table from which the row/column will be moved.
- origin_index (int, required): The index of the row/column to be moved.
- target_table_name (str, required): The name of the table to which the row/column will be moved.
- target_index (int, required): The index at which the row/column will be moved in the target table.
- axis (str or int, required):
    - 0 or "index": Indicates to move a row.
    - 1 or "columns": Indicates to move a column.\
Output:
- The new version of the origin table.
- The new version of the target table.\
"""
