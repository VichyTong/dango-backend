from dsl.functions import DangoFunction


class DangoInsert(DangoFunction):
    def __init__(self):
        super().__init__(function_type="column_row")

    def definition(self):
        return """\
insert(table_name, index, index_name, axis): Inserts an empty row or column at the specified index in the table. Other rows or columns will be move down or right.
Parameters:
- table_name (str, required): The name of the table to insert the row/column into.
- index (int, required): The final position at which the new row/column will be inserted. For example, if index = 1, the new row/column will be at position 1.
- index_name (str, required): The name of the new row/column.
- axis (str or int, required):
    - 0 or "index": Indicates to insert a row.
    - 1 or "columns": Indicates to insert a column.\
"""
