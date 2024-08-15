import pandas as pd

from functions import DangoFunction

class DangoSplit(DangoFunction):
    def __init__(self, table, label, delimiter, axis=0):
        super().__init__(function_type="A")
        self.table = table
        self.label = label
        self.delimiter = delimiter
        self.axis = axis

    def definition(self):
        return """\
split(table, label, delimiter, axis, new_column=None): Separates rows by unnesting elements in a column or splits columns based on a delimiter within the column values, depending on the specified axis.
Parameters:
- table_name (str, required): The table in which the rows/columns will be split.
- label (str or int, required): The label of the row/column to be split.
- delimiter (str, required): The delimiter to use for splitting the rows/columns.
- axis (str or int, required):
    - 0 or 'index' for row splitting
    - 1 or 'columns' for column splitting.
- new_column (list of str, optional): The label of the column to split when mode is 'columns'. Required for 'columns' mode.\
"""

    def execute(self):
        """
        Splits rows or columns in the given table based on a specified delimiter.

        Parameters:
        - table: The DataFrame in which the rows/columns will be split.
        - label: The label of the row/column to be split.
        - delimiter: The delimiter to use for splitting the rows/columns.
        - axis:
        - 0 or 'index' for row splitting
        - 1 or 'columns' for column splitting.
        """

        def split_rows(df, label, delimiter):
            new_rows = []
            for index, row in df.iterrows():
                parts = row[label].split(delimiter)
                for part in parts:
                    new_row = row.copy()
                    new_row[label] = part.strip()
                    new_rows.append(new_row)
            return pd.DataFrame(new_rows)

        def split_columns(df, label, delimiter):
            new_columns = df[label].str.split(delimiter, expand=True)
            new_columns.columns = [
                f"{label}_part{i+1}" for i in range(new_columns.shape[1])
            ]
            df = df.drop(columns=[label])
            df = pd.concat([df, new_columns], axis=1)
            return df

        axis = self.classify_axis(self.axis)

        if axis == 0:
            return split_rows(self.table, self.label, self.delimiter)
        elif axis == 1:
            return split_columns(self.table, self.label, self.delimiter)
        else:
            raise ValueError("Invalid axis. Use 0 for rows or 1 for columns.")

    def to_natural_language(self):
        if self.classify_axis(self.axis) == 0:
            return f"Split row '{self.label}' into multiple rows using the delimiter '{self.delimiter}'."
        else:
            return f"Split column '{self.label}' into multiple columns using the delimiter '{self.delimiter}'."
