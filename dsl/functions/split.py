from dsl.functions import DangoFunction


class DangoSplit(DangoFunction):
    def __init__(self):
        super().__init__(function_type="string_operation")

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
