import pandas as pd
from functions import DangoFunction

class DangoDivide(DangoFunction):
    def __init__(self):
        super().__init__(function_type="A")

    def definition(self):
        return """\
divide(table_name, by, axis): Divides the table by the specific values of a row or column, return a list of tables.
Parameters:
- table (str, required): table to be divided.
- by(int/str, required): The label of a row or column.
- axis (str or int, required):
    - 0 or "index": Indicates to divide the table by a row.
    - 1 or "columns": Indicates to divide the table by a column.\
"""

    def execute(self, table, by, axis=0):
        """
        Divides the table by the specific values of a row or column.

        Parameters:
        - table (pd.DataFrame): DataFrame to be divided.
        - by (str or int): Column/Row name to group the table by.
        - axis (str or int):
            - 0 or "index": Indicates to divide the table by a row.
            - 1 or "columns": Indicates to divide the table by a column.
        """
        axis = self.classify_axis(axis)

        if axis == 1:
            groups = table.groupby(by)
        elif axis == 0:
            groups = table.T.groupby(by).T

        result = []
        for group in groups:
            result.append(
                {
                    "unique_value": group[0],
                    "data": group[1].reset_index(drop=True),
                }
            )
        return result
