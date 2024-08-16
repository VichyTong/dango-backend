from dsl.functions import DangoFunction


class DangoTest(DangoFunction):
    def __init__(self):
        super().__init__(function_type="summarization")

    def definition(self):
        return """\
test(table_name, label_a, label_b, strategy, axis): Returns a new result table by comparing two labels using the specified strategy.
Parameters:
- table_name (str, required): table on which the test will be performed.
- label_a (str or int, required): The label of the first row/column to be tested.
- label_b (str or int, required): The label of the second row/column to be tested.
- strategy (str, required): The statistical test to perform ('t-test', 'z-test', 'chi-squared').
- axis (str or int, required):
    - 0 or "index": Indicates to test rows.
    - 1 or "columns": Indicates to test columns.\
"""
