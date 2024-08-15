from functions import DangoFunction

class DangoDrop(DangoFunction):
    def __init__(self, table, label, axis=0, condition=None):
        super().__init__(function_type="A")
        self.table = table
        self.label = label
        self.axis = axis
        self.condition = condition

    def definition(self):
        return """\
drop(table_name, label, axis): Drops one or more rows or columns in the table.
Parameters:
- table_name (str, required): The name of the table to drop the row/column from.
- label (str or int or list[str] or list[int], required): The label or list of labels of the row/column to be dropped.
- axis (str or int, required):
    - 0 or "index": Indicates to drop one or more rows.
    - 1 or "columns": Indicates to drop one or more columns.\
"""

    def execute(self):
        """
        Drops rows or columns in the table.

        Parameters:
        - table: DataFrame from which the row(s)/column(s) will be dropped.
        - label: The label(s) of the row(s)/column(s) to be dropped. For rows, this is the index label; for columns, this is the column name. It can be a single label or a list of labels.
        - axis:
        - 0 or "index": Indicates a row operation.
        - 1 or "columns": Indicates a column operation.
        """

        axis = self.classify_axis(axis)

        if self.condition is not None:
            exec(self.condition)
            boolean_indexing = locals()["boolean_indexing"]
            if axis == 0:
                index_to_drop = self.table.index[boolean_indexing(self.table)]
                self.table.drop(index=index_to_drop, axis=axis, inplace=True)
            else:
                columns_to_drop = self.table.columns[boolean_indexing(self.table)]
                self.table.drop(columns=columns_to_drop, axis=axis, inplace=True)
        else:
            # Ensure label is a list
            if not isinstance(label, list):
                label = [label]

            # Dropping columns
            if axis == 1:
                missing_columns = [col for col in label if col not in self.table.columns]
                if missing_columns:
                    raise ValueError(
                        f"Column(s) {missing_columns} do not exist in the DataFrame."
                    )
                self.table.drop(labels=label, axis=axis, inplace=True)

            # Dropping rows
            else:
                label = [str(int(l) - 1) for l in label]
                missing_rows = [l for l in label if l not in self.table.index]
                if missing_rows:
                    raise ValueError(
                        f"Row index(es) {missing_rows} do not exist in the DataFrame."
                    )
                self.table.drop(labels=label, axis=axis, inplace=True)
        return self.table
    
    def to_natural_language(self):
        if self.classify_axis(self.axis) == 0:
            return f"Drop row(s) with label(s) {self.label} from the table."
        else:
            return f"Drop column(s) with label(s) {self.label} from the table."
