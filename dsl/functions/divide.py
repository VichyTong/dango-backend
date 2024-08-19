from dsl.functions import DangoFunction


class DangoDivide(DangoFunction):
    def __init__(self):
        super().__init__(function_type="column_row")

    def definition(self):
        return """\
divide(table, by, axis): Divides the table by the specific values of a row or column, return a list of tables.
Parameters:
- table (DataFrame, required): table to be divided.
- by(int/str, required): The label of a row or column.
- axis (str or int, required):
    - 0 or "index": Indicates to divide the table by a row. If the by is a row label, you should set axis to 0.
    - 1 or "columns": Indicates to divide the table by a column. If the by is a column label, you should set axis to 1.
Output:
- A list of pandas DataFrames.\
"""
