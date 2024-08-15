import pandas as pd

from functions import DangoFunction


class DangoInsert(DangoFunction):
    def __init__(self, table, index, index_name="new_column", axis=0):
        super().__init__(function_type="A")
        self.table = table
        self.index = index
        self.index_name = index_name
        self.axis = axis

    def definition(self):
        return """\
insert(table_name, index, index_name, axis): Inserts an empty row or column at the specified index in the table. Other rows or columns will be move down or right.
Parameters:
- table_name (str, required): The name of the table to insert the row/column into.
- index (int, required): The final position at which the new row/column will be inserted. For example, if index = 1, the new row/column will be at position 1.
- index_name (str, required): The name of the new row/column.
- axis (str or int, required):
    - 0 or "index": Indicates to insert a row.
    - 1 or "columns": Indicates to insert a column.\
"""

    def execute(self):
        """
        Inserts an empty row or column at the specified index in the table.

        Parameters:
        - table: DataFrame in which the row/column will be inserted.
        - index: The index at which the row/column will be inserted.
        - index_name: The name of the new row/column.
        - axis:
        - 0 or "index": Indicates a row operation.
        - 1 or "columns": Indicates a column operation.
        """

        axis = self.classify_axis(axis)
        index = index - 1

        if axis == 1:
            if self.index_name in table.columns:
                raise ValueError(
                    f"Column {self.index_name} already exists in the DataFrame."
                )
            table.insert(
                loc=index, column=self.index_name, value=pd.Series([None] * len(table))
            )
        else:
            if self.index_name in table.index:
                raise ValueError(
                    f"Row {self.index_name} already exists in the DataFrame."
                )
            new_row = pd.DataFrame([None] * len(table.columns)).T
            new_row.columns = table.columns
            new_row.index = [self.index_name]
            table = pd.concat(
                [table.iloc[:index], new_row, table.iloc[index:]]
            ).reset_index(drop=True)

        return table

    def to_natural_language(self):
        if self.classify_axis(self.axis) == 0:
            return f"Insert an empty row at index {self.index} in the table."
        else:
            return f"Insert an empty column at index {self.index} in the table."
