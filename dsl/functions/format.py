import re
import pandas as pd
from functions import DangoFunction

class DangoFormat(DangoFunction):
    def __init__(self):
        super().__init__(function_type="A")

    def definition(self):
        return """\
format(table_name, label, pattern, replace_with, axis): Formats the values in a row or column based on the specified pattern and replace_with using re.sub().
Parameters:
- table (str, required): DataFrame in which the row/column will be formatted.
- label (str or int, required): The label of the row/column to be formatted.
- pattern (str, required): The format regex pattern to apply to the values, You can use group syntax.
- replace_with (str, required): The string or backreference to replace the matched pattern with.
- axis (str or int, required):
    - 0 or "index": Indicates to format a row.
    - 1 or "columns": Indicates to format a column.\
"""

    def execute(self, table, label, pattern, replace_with="", axis=0):
        """
        Formats the values in a row or column based on the specified pattern.

        Parameters:
        - table: DataFrame in which the row/column will be formatted.
        - label: The label of the row/column to be formatted.
        - pattern: The format regex pattern to apply to the values.
        - replace_with: The string to replace the matched pattern with.
        - axis: 0 or "index" for a row operation, 1 or "columns" for a column operation.
        """
        axis = self.classify_axis(axis)

        if axis == 1:
            if label not in table.columns:
                raise ValueError(f"Column '{label}' does not exist in the DataFrame.")
            table[label] = table[label].apply(
                lambda x: re.sub(pattern, replace_with, str(x))
            )
        else:
            if label not in table.index:
                raise ValueError(f"Row '{label}' does not exist in the DataFrame.")
            table.loc[label] = table.loc[label].apply(
                lambda x: re.sub(pattern, replace_with, str(x))
            )

        return table
