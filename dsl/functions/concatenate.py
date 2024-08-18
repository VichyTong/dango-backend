from dsl.functions import DangoFunction


class DangoConcatenate(DangoFunction):
    def __init__(self):
        super().__init__(function_type="string_operation")

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
    - 1 or "columns": Indicates to concatenate columns.
Output:
- A new table with the concatenated row/column.\
"""
