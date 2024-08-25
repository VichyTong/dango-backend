from dsl.functions import DangoFunction


class DangoFill(DangoFunction):
    def __init__(self):
        super().__init__(function_type="column_row")

    def definition(self):
        return """\
fill(table, method, labels, axis): Fills missing values in the table using the specified method.
Parameters:
- table (DataFrame, required): The table in which missing values will be filled.
- method (str, required): The method to use for filling missing values. Choose from 'value', 'mean', 'median', 'mode', 'ffill', 'bfill', 'interpolate'.
- labels (list[str or int] or int or str, required): The label or list of labels of the row(s) or column(s) where missing values will be filled.
- axis (str or int, required):
    - 0 or "index": Indicates that labels are row labels.
    - 1 or "columns": Indicates that labels are column labels.
Output:
- A pandas DataFrame.\
"""
