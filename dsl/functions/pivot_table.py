from dsl.functions import DangoFunction

class DangoPivotTable(DangoFunction):
    def __init__(self):
        super().__init__(function_type="column_row")

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
