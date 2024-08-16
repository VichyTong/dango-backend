from dsl.functions import DangoFunction


class DangoAggregate(DangoFunction):
    def __init__(self):
        super().__init__(function_type="summarization")

    def definition(self):
        return """\
aggregate(table_name, functions, axis): Aggregates the table using the specified function.
Parameters:
- table_name (str, required): table to be aggregated.
- functions (dict, required): Keys are names of rows or columns, and values are lists of function names. Example: {'A': ['sum', 'mean'], 'B': ['min', 'max']}.
- axis (str or int, required):
    - 0 or "index": Applies the aggregate operations on rows, the keys in the functions dict is some row names.
    - 1 or "columns": Applies the aggregate operations on columns, the keys in the functions dict is some column names.\
"""
