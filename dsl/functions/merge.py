from dsl.functions import DangoFunction


class DangoMerge(DangoFunction):
    def __init__(self):
        super().__init__(function_type="table")

    def definition(self):
        return """\
merge(table_name_a, table_name_b, how="outer", on=None, axis): Merges two tables based on a common column or along columns.
Parameters:
- table_name_a (str, required): First table
- table_name_b (str, required): Second table
- how(str, required): Type of merge to be performed. Options are 'left', 'right', 'outer', 'inner'. Default is 'outer'.
- on(str, required): Column or index level names to join on. Must be found in both DataFrames. If not provided and the DataFrames have a common column, will default to the intersection of the columns in the DataFrames.
- axis(str or int, required): Axis to merge along. 0 or "index" for row-wise, 1 or "column" for column-wise. Default is 0.\
"""
