from dsl.functions import DangoFunction


class DangoSubtable(DangoFunction):
    def __init__(self):
        super().__init__(function_type="table")

    def definition(self):
        return """\
subtable(table_name, label_list, new_name, axis): Returns a new table with only the specified rows or columns.
Parameters:
- table_name (str, required): The name of the table to extract the rows/columns from.
- label_list (list[str/int], required): The list of row/column labels to extract.
- new_name (str, required): The name of the new table.
- axis (str or int, required):
    - 0 or "index": Indicates to extract rows. The label_list contains row indexes.
    - 1 or "columns": Indicates to extract columns. The label_list contains column names.
"""
