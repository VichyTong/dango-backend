import pandas as pd

from functions import DangoFunction

class DangoAggregate(DangoFunction):
    def __init__(self, table, functions, axis=0):
        super().__init__(function_type="A")
        self.table = table
        self.functions = functions
        self.axis = axis
    
    def definition(self):
        return """\
aggregate(table_name, functions, axis): Aggregates the table using the specified function.
Parameters:
- table_name (str, required): table to be aggregated.
- functions (dict, required): Keys are names of rows or columns, and values are lists of function names. Example: {'A': ['sum', 'mean'], 'B': ['min', 'max']}.
- axis (str or int, required):
    - 0 or "index": Applies the aggregate operations on rows, the keys in the functions dict is some row names.
    - 1 or "columns": Applies the aggregate operations on columns, the keys in the functions dict is some column names.\
"""

    def execute(self):
        """
        Aggregates the table using the specified function.

        Parameters:
        - table: DataFrame to be aggregated.
        - functions: A function or list of functions to apply to each column/row.
        - axis:
        - 0 or "index": Indicates a row operation.
        - 1 or "columns": Indicates a column operation.
        """

        axis = self.classify_axis(self.axis)

        # Invert axis to match the behavior of aggregation
        if axis == 0:
            axis = 1
        elif axis == 1:
            axis = 0

        try:
            result = self.table.agg(self.functions, axis=axis)
            if isinstance(result, pd.Series):
                result = (
                    result.to_frame().transpose() if axis == 0 else result.to_frame()
                )
        except Exception as e:
            raise ValueError(f"Error applying aggregation functions: {e}")

        return result

    def to_natural_language(self):
        axis_text = "row-wise" if self.classify_axis(self.axis) == 0 else "column-wise"
        return f"Aggregate the table {axis_text} using the function(s): {self.functions}."
