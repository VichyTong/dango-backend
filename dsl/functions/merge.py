from functions import DangoFunction
import pandas as pd

class DangoMerge(DangoFunction):
    def __init__(self, table_a, table_b, how="outer", on=None, axis=0):
        super().__init__(function_type="A")
        self.table_a = table_a
        self.table_b = table_b
        self.how = how
        self.on = on
        self.axis = axis

    def definition(self):
        return """\
merge(table_name_a, table_name_b, how="outer", on=None, axis): Merges two tables based on a common column or along columns.
Parameters:
- table_name_a (str, required): First table
- table_name_b (str, required): Second table
- how(str, required): Type of merge to be performed. Options are 'left', 'right', 'outer', 'inner'. Default is 'outer'.
- on(str, required): Column or index level names to join on. Must be found in both DataFrames. If not provided and the DataFrames have a common column, will default to the intersection of the columns in the DataFrames.
- axis(str or int, required): Axis to merge along. 0 or "index" for row-wise, 1 or "column" for column-wise. Default is 0.\
"""

    def execute(self):
        """
        Merges two tables based on a common column or along columns.

        Parameters:
        - table_a: First DataFrame to be merged.
        - table_b: Second DataFrame to be merged.
        - how: Type of merge to be performed. Options are 'left', 'right', 'outer', 'inner'. Default is 'outer'.
        - on: Column or index level names to join on. Must be found in both DataFrames. If not provided and the DataFrames
            have a common column, it will default to the intersection of the columns in the DataFrames.
        - axis: Axis to concatenate along. 0 or "index" for row-wise, 1 or "columns" for column-wise. Default is 0.
        """
        axis = self.classify_axis(self.axis)

        if axis == 0:  # Row-wise merge
            return pd.concat([self.table_a, self.table_b], ignore_index=True)
        elif axis == 1:  # Column-wise merge
            return pd.merge(self.table_a, self.table_b, how=self.how, on=self.on)

    def to_natural_language(self):
        if self.classify_axis(self.axis) == 0:
            return "Merge the two tables row-wise."
        else:
            merge_type = f"{self.how} merge" if self.how else "merge"
            on_clause = f" on '{self.on}'" if self.on else ""
            return f"Perform a {merge_type} of the two tables{on_clause}."
