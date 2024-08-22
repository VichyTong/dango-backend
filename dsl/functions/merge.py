from dsl.functions import DangoFunction


class DangoMerge(DangoFunction):
    def __init__(self):
        super().__init__(function_type="table")

    def definition(self):
        return """\
merge(table_a, table_b, how='outer', on=None): Merges two tables based on a common column.
Parameters:
- table_a (DataFrame, required): First table to merge.
- table_b (DataFrame, required): Second table to merge.
- how(str, required): Type of merge to be performed. Options are 'left', 'right', 'outer', 'inner' or 'fuzzy'. Default is 'outer'.
- on(str, required): Column or index level names to join on. Must be found in both tables.
Output:
- A pandas DataFrame.\
"""
