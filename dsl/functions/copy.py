from functions import DangoFunction
import pandas as pd

class DangoCopy(DangoFunction):
    def __init__(self, origin_table, origin_index, target_table, target_index, target_label_name=None, axis=0):
        super().__init__(function_type="A")
        self.origin_table = origin_table
        self.origin_index = origin_index
        self.target_table = target_table
        self.target_index = target_index
        self.target_label_name = target_label_name
        self.axis = axis

    def definition(self):
        return """\
copy(origin_table_name, origin_index, target_table_name, target_index, target_label_name, axis): Copies a row or column from the origin table to the target table at the specified index.
Parameters:
- origin_table_name (str, required): The name of the table from which the row/column will be copied.
- origin_index (int, required): The index of the row/column to be copied.
- target_table_name (str, required): The name of the table to which the row/column will be copied.
- target_index (int, required): The index at which the row/column will be copied in the target table.
- target_label_name (str, required): The name of the new row/column in the target table.
- axis (str or int, required):
    - 0 or "index": Indicates to copy a row.
    - 1 or "columns": Indicates to copy a column.\
"""

    def execute(self):
        """
        Copies a row or column from the origin table to the target table at the specified index.

        Parameters:
        - origin_table: DataFrame from which the row/column will be copied.
        - origin_index: The index of the row/column to be copied. Index is 1-based.
        - target_table: DataFrame to which the row/column will be copied.
        - target_index: The index at which the row/column will be copied in the target DataFrame. Index is 1-based.
        - target_label_name: The name of the new row/column in the target DataFrame. If None, the index will be used.
        - axis:
        - 0 or "index": Indicates a row operation.
        - 1 or "columns": Indicates a column operation.
        """
        # Adjust indices to be zero-based
        origin_index = self.origin_index - 1
        target_index = self.target_index - 1

        axis = self.classify_axis(self.axis)

        if axis == 0:  # Copy row
            row = self.origin_table.iloc[origin_index]
            if self.target_label_name is not None:
                row.name = self.target_label_name
            else:
                row.name = target_index
            self.target_table = pd.concat(
                [
                    self.target_table.iloc[:target_index],
                    row.to_frame().T,
                    self.target_table.iloc[target_index:],
                ]
            ).reset_index(drop=True)
        elif axis == 1:  # Copy column
            col = self.origin_table.iloc[:, origin_index]
            if self.target_label_name is not None:
                col.name = self.target_label_name
            else:
                col.name = target_index
            self.target_table = pd.concat(
                [
                    self.target_table.iloc[:, :target_index],
                    col.to_frame(),
                    self.target_table.iloc[:, target_index:],
                ],
                axis=1,
            )

        return self.origin_table, self.target_table

    def to_natural_language(self):
        if self.classify_axis(self.axis) == 0:
            return f"Copy row {self.origin_index} from the origin table to row {self.target_index} in the target table."
        else:
            return f"Copy column {self.origin_index} from the origin table to column {self.target_index} in the target table."
