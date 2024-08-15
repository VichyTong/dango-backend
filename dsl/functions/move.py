from functions import DangoFunction
import pandas as pd

class DangoMove(DangoFunction):
    def __init__(self, origin_table, origin_index, target_table, target_index, axis=0):
        super().__init__(function_type="A")
        self.origin_table = origin_table
        self.origin_index = origin_index
        self.target_table = target_table
        self.target_index = target_index
        self.axis = axis

    def definition(self):
        return """\
move(origin_table_name, origin_index, target_table_name, target_index, axis): Moves a row or column from the origin table to the target table.
Parameters:
- origin_table_name (str, required): The name of the table from which the row/column will be moved.
- origin_index (int, required): The index of the row/column to be moved.
- target_table_name (str, required): The name of the table to which the row/column will be moved.
- target_index (int, required): The index at which the row/column will be moved in the target table.
- axis (str or int, required):
    - 0 or "index": Indicates to move a row.
    - 1 or "columns": Indicates to move a column.\
"""

    def execute(self):
        """
        Moves a row or column from the origin table to the target table.

        Parameters:
        - origin_table: DataFrame from which the row/column will be moved.
        - origin_index: The index of the row/column to be moved. Index is 1-based.
        - target_table: DataFrame to which the row/column will be moved.
        - target_index: The index at which the row/column will be inserted in the target DataFrame. Index is 1-based.
        - axis:
        - 0 or "index": Indicates a row operation.
        - 1 or "columns": Indicates a column operation.
        """
        # Adjust indices to be zero-based
        origin_index = self.origin_index - 1
        target_index = self.target_index - 1

        axis = self.classify_axis(self.axis)

        if axis == 0:  # Move row
            row = self.origin_table.iloc[origin_index]
            self.origin_table = self.origin_table.drop(self.origin_table.index[origin_index])
            self.target_table = pd.concat(
                [
                    self.target_table.iloc[:target_index],
                    row.to_frame().T,
                    self.target_table.iloc[target_index:],
                ]
            ).reset_index(drop=True)
        elif axis == 1:  # Move column
            col = self.origin_table.iloc[:, origin_index]
            self.origin_table = self.origin_table.drop(self.origin_table.columns[origin_index], axis=1)
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
            return f"Move row {self.origin_index} from the origin table to row {self.target_index} in the target table."
        else:
            return f"Move column {self.origin_index} from the origin table to column {self.target_index} in the target table."
