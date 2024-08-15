import pandas as pd
from functions import DangoFunction

class DangoPivotTable(DangoFunction):
    def __init__(self):
        super().__init__(function_type="A")

    def definition(self):
        return """\
pivot_table(table_name, index, columns, values, aggfunc): Reshapes the table so that each unique 'columns' value becomes a separate column, with the 'index' values as row headers, and the corresponding 'values' filled in their respective cells.
Parameters:
- table_name (str, required): The table to pivot.
- index (str, required): The column name to use as the new row headers.
- columns (str, required): The column name to use as the new column headers.
- values (str, required): The column name whose values will fill the new table.
- aggfunc (str, required): The aggregation function to apply to the values. Common options are 'first', 'sum', 'mean', etc.
"""

    def execute(self, table, index, columns, values, aggfunc="first"):
        """
        Reshapes the table based on the specified index, columns, values, and aggregation function.

        Parameters:
        - table (pd.DataFrame): The DataFrame to pivot.
        - index (str): The column name to use as the new row headers.
        - columns (str): The column name to use as the new column headers.
        - values (str): The column name whose values will fill the new table.
        - aggfunc (str): The aggregation function to apply to the values. Common options are 'first', 'sum', 'mean', etc.

        Returns:
        - pd.DataFrame: The pivoted table.
        """
        pivot_df = table.pivot_table(
            index=index, columns=columns, values=values, aggfunc=aggfunc
        ).reset_index()
        return pivot_df