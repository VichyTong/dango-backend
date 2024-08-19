from dsl.functions import DangoFunction


class DangoTest(DangoFunction):
    def __init__(self):
        super().__init__(function_type="summarization")

    def definition(self):
        return """\
test(table_a, label_a, table_b, label_b, strategy, axis): Returns a tuple (statistic, p_value) by comparing two labels using the specified strategy.
Parameters:
- table_a (DataFrame, required): table A on which the test will be performed.
- label_a (str or int, required): The label of the first row/column to be tested.
- table_b (DataFrame, required): table B on which the test will be performed.
- label_b (str or int, required): The label of the second row/column to be tested.
- strategy (str, required): The statistical test to perform ('t-test', 'z-test', 'chi-squared', 'pearson-correlation').
- axis (str or int, required):
    - 0 or "index": Indicates to test rows.
    - 1 or "columns": Indicates to test columns.
Output:
- A tuple (statistic, p_value).\
"""
