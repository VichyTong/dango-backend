from dsl.functions import DangoFunction


class DangoSplit(DangoFunction):
    def __init__(self):
        super().__init__(function_type="string_operation")

    def definition(self):
        return """\
split(table, label, delimiter, new_label_list, axis): Separates rows or columns based on a string delimiter within the values.
Parameters:
- table (DataFrame, required): The table in which the rows/columns will be split.
- label (str or int, required): The label of the row/column to be split.
- delimiter (str, required): The delimiter to use for splitting the rows/columns.
- new_label_list (list[str or int], required): The list of labels for the new rows/columns created by the split.
- axis (str or int, required):
    - 0 or 'index' for row splitting
    - 1 or 'columns' for column splitting.
Output:
- A pandas DataFrame.\
"""
