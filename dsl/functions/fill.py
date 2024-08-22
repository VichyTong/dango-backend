from dsl.functions import DangoFunction


class DangoFill(DangoFunction):
    def __init__(self):
        super().__init__(function_type="column_row")

    def definition(self):
        return """\
fill(table, method, labels, axis): Fills missing values in the table using the specified method.
Parameters:
- table (DataFrame, required): Table to fill missing values.
- method (str, required): The method to use for filling missing values. Choose from 'value', 'mean', 'median', 'mode', 'ffill', 'bfill', 'interpolate'.
- labels (list[str or int] or int or str, required): The label of labels list of the row(s)/column(s) to fill missing values.
- axis (str or int, required):
    - 0 or "index": Indicates to fill missing values by rows.
    - 1 or "columns": Indicates to fill missing values by columns.
Output:
- A pandas DataFrame.\
"""
