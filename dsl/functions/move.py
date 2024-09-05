from dsl.functions import DangoFunction


class DangoMove(DangoFunction):
    def __init__(self):
        super().__init__(function_type="column_row")

    def definition(self):
        return """\
move(origin_table, origin_label, target_table, target_label, axis): Moves a row or column from the origin table to the target table.
Parameters:
- origin_table (DataFrame, required): The table from which the row or column will be moved.
- origin_label (int or str, required): The index or name of the row or column to be moved in the origin table.
- target_table (DataFrame, required): The table to which the row or column will be moved.
- target_label (int or str, required): The index or name at which the row or column will be inserted in the target table.
- axis (str or int, required):
    - 0 or "index": Indicates that a row will be moved.
    - 1 or "columns": Indicates that a column will be moved.
Output:
- A pandas DataFrame containing the updated origin table with the row or column removed.
- A pandas DataFrame containing the updated target table with the row or column added.\
"""
