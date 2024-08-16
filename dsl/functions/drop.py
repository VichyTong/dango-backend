from dsl.functions import DangoFunction


class DangoDrop(DangoFunction):
    def __init__(self):
        super().__init__(function_type="column_row")

    def definition(self):
        return """\
drop(table_name, label, axis): Drops one or more rows or columns in the table.
Parameters:
- table_name (str, required): The name of the table to drop the row/column from.
- label (str or int or list[str] or list[int], required): The label or list of labels of the row/column to be dropped.
- axis (str or int, required):
    - 0 or "index": Indicates to drop one or more rows.
    - 1 or "columns": Indicates to drop one or more columns.\
"""
