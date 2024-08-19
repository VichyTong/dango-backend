from dsl.functions import DangoFunction


class DangoFill(DangoFunction):
    def __init__(self):
        super().__init__(function_type="column_row")

    def definition(self):
        return """\
fill(table, method, column=None): Fills missing values in the table using the specified method.
Parameters:
- table (DataFrame, required): Table to fill missing values.
- method (str, required): The method to use for filling missing values. Choose from 'value', 'mean', 'median', 'mode', 'ffill', 'bfill', 'interpolate'.
- column (str or list[str], optional): The column or columns to fill missing values in. If None, missing values in all columns will be filled.
Output:
- A pandas DataFrame.\
"""
