from dsl.functions import DangoFunction


class DangoTranspose(DangoFunction):
    def __init__(self, table):
        super().__init__(function_type="table")
        self.table = table

    def definition(self):
        return """\
transpose(table): Transposes the given table.
Parameters:
- table (DataFrame, required): The table to be transposed.
Output:
- A pandas DataFrame.\
"""
