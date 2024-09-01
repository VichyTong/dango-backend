from dsl.functions import DangoFunction


class DangoFill(DangoFunction):
    def __init__(self):
        super().__init__(function_type="column_row")

    def definition(self):
        return """\
fill(table, method, labels, axis): Fills missing values in the table using the specified method.
Parameters:
- table (DataFrame, required): The table in which missing values will be filled.
- labels (list[str or int] or int or str or "ALL", required): The label or list of labels where missing values will be filled. If the value is "ALL", all missing values in the table will be filled.
- method (str, required): The method to use for filling missing values. Choose from 'value', 'mean', 'median', 'mode', 'ffill', 'bfill', 'interpolate'.
- axis (str or int, required):
    - 0 or "index": Indicates that labels correspond to row labels, and filling will be applied across rows.
    - 1 or "columns": Indicates that labels correspond to column labels, and filling will be applied across columns.
Output:
- A pandas DataFrame.\
"""
