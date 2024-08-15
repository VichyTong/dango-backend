import pandas as pd
import numpy as np
from functions import DangoFunction

class DangoRearrange(DangoFunction):
    def __init__(self):
        super().__init__(function_type="A")

    def definition(self):
        return """\
rearrange(table_name, by_values=None, by_array=None, axis): Rearranges the rows or columns of the table based on the specified order.
Parameters:
- table_name (str, required): table to be rearranged.
- by_values (str, optional): If this parameter is set, the rows/columns will be rearranged based on the values in the specified row/column.
- by_array (str or list[str/int], optional): If this parameter is set, the rows/columns will be rearranged based on the order of the values in the array.
- axis (str or int, required):
    - 0 or "index": Indicates to rearrange rows. Rows will be rearranged based on the values in the specified row/column or the order in the array.
    - 1 or "columns": Indicates to rearrange columns. Columns will be rearranged based on the values in the specified row/column or the order in the array.\
"""

    def execute(self, table, by_values=None, by_array=None, axis=0):
        """
        Rearranges the rows or columns of the table based on the specified order.

        Parameters:
        - table: DataFrame to be rearranged.
        - by_values: If this parameter is set, the rows/columns will be rearranged based on the values in the specified row/column.
        - by_array: If this parameter is set, the rows/columns will be rearranged based on the order of the values in the array.
        - axis:
            - 0 or "index": Indicates a row operation.
            - 1 or "columns": Indicates a column operation.
        """

        axis = self.classify_axis(axis)

        if by_values is not None:
            if axis == 0:
                # Rearrange rows based on the values in the specified column
                sorted_indices = table[by_values].argsort()
                return table.iloc[sorted_indices]
            elif axis == 1:
                # Rearrange columns based on the values in the specified row
                sorted_indices = table.loc[by_values].argsort()
                return table.iloc[:, sorted_indices]
            else:
                raise ValueError(
                    "Axis should be 0 or 'index' for row operation, 1 or 'columns' for column operation"
                )
        elif by_array is not None:
            if axis == 0:
                # Rearrange rows based on the order of the values in the array
                return table.iloc[by_array]
            elif axis == 1:
                # Rearrange columns based on the order of the values in the array
                return table.iloc[:, by_array]
            else:
                raise ValueError(
                    "Axis should be 0 or 'index' for row operation, 1 or 'columns' for column operation"
                )
        else:
            raise ValueError("Either by_values or by_array must be provided")
