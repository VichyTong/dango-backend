import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from functions import DangoFunction

class DangoTest(DangoFunction):
    def __init__(self):
        super().__init__(function_type="A")

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

    def execute(self, table, label_a, label_b, strategy, axis=0):
        """
        Returns a new result table by comparing two labels using the specified strategy.

        Parameters:
        - table: DataFrame on which the test will be performed.
        - label_a: The label of the first row/column to be tested.
        - label_b: The label of the second row/column to be tested.
        - strategy: The statistical test to perform ('t-test', 'z-test', 'chi-squared').
        - axis:
        - 0 or "index": Indicates a row operation.
        - 1 or "columns": Indicates a column operation.
        """

        axis = self.classify_axis(axis)

        # Validate strategy
        supported_strategies = ["t-test", "z-test", "chi-squared"]
        if strategy not in supported_strategies:
            raise ValueError(
                f"Strategy '{strategy}' is not supported. Supported strategies are: {supported_strategies}"
            )

        # Perform the test between two columns
        if axis == 1:
            if label_a not in table.columns or label_b not in table.columns:
                raise ValueError(
                    "One or both specified labels do not exist in the DataFrame's columns."
                )

            # Extract the data for each column
            data_1 = table[label_a]
            data_2 = table[label_b]

        # Perform the test between two rows
        else:
            if label_a not in table.index or label_b not in table.index:
                raise ValueError(
                    "One or both specified labels do not exist in the DataFrame's index."
                )

            # Extract the data for each row
            data_1 = table.loc[label_a]
            data_2 = table.loc[label_b]

        # Perform a t-test
        if strategy == "t-test":
            test_stat, p_value = stats.ttest_ind(data_1, data_2)

        # Perform a z-test
        elif strategy == "z-test":
            z_stat, p_value = sm.stats.ztest(data_1, data_2)
            test_stat = z_stat

        # Perform a chi-squared test
        elif strategy == "chi-squared":
            # For chi-squared test, we expect the data to be categorical and in a contingency table format
            # Here we construct a contingency table from the two data sets
            data_crosstab = pd.crosstab(data_1, data_2)
            chi2_stat, p_value, dof, expected = stats.chi2_contingency(data_crosstab)
            test_stat = chi2_stat

        # Create a new table to store the test results
        result_table = pd.DataFrame(
            index=range(1), columns=["Test Statistic", "P-Value"]
        )
        result_table.iloc[0, 0] = test_stat
        result_table.iloc[0, 1] = p_value

        return result_table
