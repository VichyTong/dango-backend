from functions import DangoFunction

class DangoSwap(DangoFunction):
    def __init__(self, table_a, label_a, table_b, label_b, axis=0):
        super().__init__(function_type="A")
        self.table_a = table_a
        self.label_a = label_a
        self.table_b = table_b
        self.label_b = label_b
        self.axis = axis

    def definition(self):
        return """\
swap(table_name_a, label_a, table_name_b, label_b, axis): Swaps rows or columns between two tables.
Parameters:
- table_name_a (str, required): The first table from which the row/column will be swapped.
- label_a (str or int, required): The label of the row/column to be swapped in the first table.
- table_name_b (str, required): The second table from which the row/column will be swapped.
- label_b (str or int, required): The label of the row/column to be swapped in the second table.
- axis (str or int, required):
    - 0 or "index": Indicates to swap rows.
    - 1 or "columns": Indicates to swap columns.\
"""

    def execute(self):
        """
        Swaps rows or columns between two tables.

        Parameters:
        - table_a: The first DataFrame from which the row/column will be swapped.
        - label_a: The label of the row/column to be swapped in the first DataFrame.
        - table_b: The second DataFrame from which the row/column will be swapped.
        - label_b: The label of the row/column to be swapped in the second DataFrame.
        - axis:
        - 0 or "index": Indicates a row operation.
        - 1 or "columns": Indicates a column operation.
        """
        axis = self.classify_axis(self.axis)

        # Swapping columns
        if axis == 1:
            if self.label_a not in self.table_a.columns or self.label_b not in self.table_b.columns:
                raise ValueError(
                    "One or both specified column labels do not exist in the respective DataFrames."
                )

            # Use temporary column names to avoid duplicates
            temp_label_a = "__temp__" + self.label_a
            temp_label_b = "__temp__" + self.label_b

            self.table_a.rename(columns={self.label_a: temp_label_a}, inplace=True)
            self.table_b.rename(columns={self.label_b: temp_label_b}, inplace=True)

            # Swap the columns
            self.table_a[temp_label_a], self.table_b[temp_label_b] = (
                self.table_b[temp_label_b],
                self.table_a[temp_label_a],
            )

            self.table_a.rename(columns={temp_label_a: self.label_b}, inplace=True)
            self.table_b.rename(columns={temp_label_b: self.label_a}, inplace=True)

        # Swapping rows
        else:
            label_a = int(self.label_a) - 1
            label_b = int(self.label_b) - 1

            if label_a not in self.table_a.index or label_b not in self.table_b.index:
                raise ValueError(
                    "One or both specified row labels do not exist in the respective DataFrames."
                )

            # Swap the rows between the two DataFrames
            temp_row_a = self.table_a.loc[label_a].copy()
            self.table_a.loc[label_a] = self.table_b.loc[label_b]
            self.table_b.loc[label_b] = temp_row_a

        return self.table_a, self.table_b

    def to_natural_language(self):
        if self.classify_axis(self.axis) == 0:
            return f"Swap row {self.label_a} from the first table with row {self.label_b} from the second table."
        else:
            return f"Swap column {self.label_a} from the first table with column {self.label_b} from the second table."
