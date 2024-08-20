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
- how(str, required): Type of merge to be performed. Options are 'left', 'right', 'outer', 'inner'. Default is 'outer'.
- on(str, required): Column or index level names to join on. Must be found in both DataFrames. If not provided and the DataFrames have a common column, will default to the intersection of the columns in the DataFrames.
Output:
- A pandas DataFrame.\
"""
