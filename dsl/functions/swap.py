from dsl.functions import DangoFunction


class DangoSwap(DangoFunction):
    def __init__(self):
        super().__init__(function_type="column_row")

    def definition(self):
        return """\
swap(table_name_a, label_a, table_name_b, label_b, axis): Swaps rows or columns between two tables.
Parameters:
- table_name_a (str, required): The first table from which the row/column will be swapped.
- label_a (str or int, required): The label of the row/column to be swapped in the first table.
- table_name_b (str, required): The second table from which the row/column will be swapped.
- label_b (str or int, required): The label of the row/column to be swapped in the second table.
- axis (str or int, required):
    - 0 or "index": Indicates to swap rows.
    - 1 or "columns": Indicates to swap columns.\
"""
