from dsl.functions import DangoFunction


class DangoFormat(DangoFunction):
    def __init__(self):
        super().__init__(function_type="string_operation")

    def definition(self):
        return """\
format(table_name, label, pattern, replace_with, axis): Formats the values in a row or column based on the specified pattern and replace_with using re.sub().
Parameters:
- table (str, required): DataFrame in which the row/column will be formatted.
- label (str or int, required): The label of the row/column to be formatted.
- pattern (str, required): The format regex pattern to apply to the values, You can use group syntax.
- replace_with (str, required): The string or backreference to replace the matched pattern with.
- axis (str or int, required):
    - 0 or "index": Indicates to format a row.
    - 1 or "columns": Indicates to format a column.\
"""
