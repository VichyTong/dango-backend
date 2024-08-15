from functions import DangoFunction

class DangoAssign(DangoFunction):
    def __init__(self, table, start_row_index, end_row_index, start_column_index, end_column_index, values):
        super().__init__(function_type="A")
        self.table = table
        self.start_row_index = start_row_index
        self.end_row_index = end_row_index
        self.start_column_index = start_column_index
        self.end_column_index = end_column_index
        self.values = values

    def definition(self):
        return """\
assign(table_name, start_row_index, end_row_index, start_column_index, end_column_index, values): Assigns constant values to specific cells in the table.
Parameters:
- table_name (str, required): The name of the table to assign the value to.
- start_row_index, end_row_index (int, required): The range of row indices to assign the value to.
- start_column_index, end_column_index (int, required): The range of column indices to assign the value to.
- values (list[list[int/float/str]] or int/float/str, required): The const value(s) to assign to the specified cell(s). Can be a single int/float/str or a list of lists of int/float/str. The order of values is from top to bottom, left to right.\
"""

    def execute(self):
        """
        Assigns a value to specific cells in the table.

        Parameters:
        - table: DataFrame in which the value will be assigned.
        - start_row_index, end_row_index: The range of row indices to assign the value to. Indices are 1-based.
        - start_column_index, end_column_index: The range of column indices to assign the value to. Indices are 1-based.
        - values: The value(s) to assign to the specified cell(s). Can be a single int/float/str or a list of lists of int/float/str.
        """
        # Adjust indices to be zero-based
        start_row_index = self.start_row_index - 1
        end_row_index = self.end_row_index - 1
        start_column_index = self.start_column_index - 1
        end_column_index = self.end_column_index - 1

        # If values is a single number, create a matrix of that value
        if isinstance(self.values, (int, float, str)):
            num_rows = end_row_index - start_row_index + 1
            num_columns = end_column_index - start_column_index + 1
            values = [[self.values] * num_columns] * num_rows
        else:
            values = self.values

        # Assign the value(s) to the specified cell(s)
        self.table.iloc[start_row_index:end_row_index + 1, start_column_index:end_column_index + 1] = values

        return self.table

    def to_natural_language(self):
        return f"Assign value(s) {self.values} to cells from row {self.start_row_index} to {self.end_row_index} and column {self.start_column_index} to {self.end_column_index} in the table."
