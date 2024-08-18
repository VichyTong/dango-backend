from dsl.functions import DangoFunction


class DangoTranspose(DangoFunction):
    def __init__(self, table):
        super().__init__(function_type="table")
        self.table = table

    def definition(self):
        return """\
transpose(table_name): Transposes the given table.
Parameters:
- table_name (str, required): table to be transposed.
Output:
- A new table with the transposed data.\
"""
