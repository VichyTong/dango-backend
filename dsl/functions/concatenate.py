from functions import DangoFunction

class DangoConcatenate(DangoFunction):
    def __init__(self, table, label_a, label_b, glue, new_label, axis=0):
        super().__init__(function_type="A")
        self.table = table
        self.label_a = label_a
        self.label_b = label_b
        self.glue = glue
        self.new_label = new_label
        self.axis = axis

    def definition(self):
        return """\
concatenate(table_name, label_a, label_b, glue, new_label, axis): Concatenates two rows or columns based on a string glue and appends the merged row or column to the table.
Parameters:
- table_name (str, required): table in which the rows/columns will be concatenated.
- label_a (str or int, required): The label of the first row/column to be concatenated.
- label_b (str or int, required): The label of the second row/column to be concatenated.
- glue (str, required): The string to be used to concatenate the two rows/columns.
- new_label (str or int, required): The label of the new row/column created by the concatenation.
- axis (str or int, required):
    - 0 or "index": Indicates to concatenate rows.
    - 1 or "columns": Indicates to concatenate columns.\
"""

    def execute(self):
        """
        Concatenates two labels and appends the merged label to the table.

        Parameters:
        - table: DataFrame in which the rows/columns will be concatenated.
        - label_a: The label of the first row/column to be concatenated.
        - label_b: The label of the second row/column to be concatenated.
        - glue: The string to be used to concatenate the two rows/columns.
        - new_label: The label of the new row/column created by the concatenation.
        - axis:
        - 0 or "index": Indicates a row operation.
        - 1 or "columns": Indicates a column operation.
        """
        axis = self.classify_axis(self.axis)

        # Merging columns
        if axis == 1:
            if self.label_a not in self.table.columns or self.label_b not in self.table.columns:
                raise ValueError(
                    "One or both column labels do not exist in the DataFrame."
                )
            if self.new_label in self.table.columns:
                raise ValueError(f"Column {self.new_label} already exists in the DataFrame.")

            # Concatenate the columns with the specified glue and create a new column
            self.table[self.new_label] = (
                self.table[self.label_a].astype(str) + self.glue + self.table[self.label_b].astype(str)
            )

        # Merging rows
        else:
            label_a = int(self.label_a) - 1
            label_b = int(self.label_b) - 1
            new_label = int(self.new_label) - 1
            if label_a not in self.table.index or label_b not in self.table.index:
                raise ValueError(
                    "One or both row labels do not exist in the DataFrame."
                )
            if new_label in self.table.index:
                raise ValueError(f"Row {new_label} already exists in the DataFrame.")

            # Concatenate the rows with the specified glue and create a new row
            new_row = (
                self.table.loc[label_a].astype(str) + self.glue + self.table.loc[label_b].astype(str)
            ).rename(new_label)
            self.table.loc[new_label] = new_row.copy()

        return self.table

    def to_natural_language(self):
        if self.classify_axis(self.axis) == 0:
            return f"Concatenate row {self.label_a} and row {self.label_b} with '{self.glue}' and create a new row labeled {self.new_label}."
        else:
            return f"Concatenate column {self.label_a} and column {self.label_b} with '{self.glue}' and create a new column labeled {self.new_label}."
