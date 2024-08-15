from functions import DangoFunction

class DangoTranspose(DangoFunction):
    def __init__(self, table):
        super().__init__(function_type="A")
        self.table = table

    def definition(self):
        return """\
transpose(table_name): Transposes the given table.
Parameters:
- table_name (str, required): table to be transposed.\
"""

    def execute(self):
        """
        Transposes the given table.

        Parameters:
        - table: DataFrame to be transposed.
        """
        transposed_table = self.table.transpose()
        return transposed_table

    def to_natural_language(self):
        return "Transpose the table, swapping rows and columns."
