from dsl.functions import DangoFunction


class DangoCopy(DangoFunction):
    def __init__(self):
        super().__init__(function_type="column_row")

    def definition(self):
        return """\
copy(origin_table, origin_index, target_table, target_index, target_label_name, axis): Copies a row or column from the origin table to the target table at the specified index.
Parameters:
- origin_table (DataFrame, required): The table from which the row/column will be copied.
- origin_index (int, required): The index of the row/column to be copied.
- target_table (DataFrame, required): The table to which the row/column will be copied.
- target_index (int, required): The index at which the row/column will be copied in the target table.
- target_label_name (str, required): The name of the row/column to be copied in the target table.
- axis (str or int, required):
    - 0 or "index": Indicates to copy a row.
    - 1 or "columns": Indicates to copy a column.
Output:
- A pandas DataFrame containing the target table with the copied row/column.\
"""
