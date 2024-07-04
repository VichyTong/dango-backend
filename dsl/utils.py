import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm


def classify_axis(axis):
    if axis not in [0, 1, "index", "columns", "0", "1"]:
        raise ValueError("Axis must be 0, 'index', 1, or 'columns'")

    # Convert string axis to numeric
    if axis == "index":
        axis = 0
    elif axis == "columns":
        axis = 1
    elif axis == "0":
        axis = 0
    elif axis == "1":
        axis = 1

    return axis


def insert(table, index, name="new_column", axis=0):
    """
    Inserts a new row or column into the given DataFrame at the specified index.

    Parameters:
    - table: DataFrame in which the row/column will be inserted.
    - index: The index at which the new row/column will be inserted.
    - name: The name of the new row/column to be inserted.
    - axis: 0 for row, 1 for column. Specifies whether to insert a row or a column.
    """
    import pandas as pd

    # Inserting a column
    if axis == 1:
        if name in table.columns:
            raise ValueError(f"Column {name} already exists in the DataFrame.")
        table.insert(loc=index, column=name, value=pd.Series([None] * len(table)))
    else:
        if name in table.index:
            raise ValueError(f"Row {name} already exists in the DataFrame.")
        new_row = pd.DataFrame([None] * len(table.columns)).T
        new_row.columns = table.columns
        new_row.index = [name]
        table = pd.concat(
            [table.iloc[:index], new_row, table.iloc[index:]]
        ).reset_index(drop=True)

    return table


def drop(table, label, axis=0):
    """
    Drops a row or column from the given DataFrame based on the label and axis.

    Parameters:
    - table: DataFrame from which the row/column will be dropped.
    - label: The label of the row/column to be dropped. For rows, this is the index label; for columns, this is the column name.
    - axis: 0 for row, 1 for column. Specifies whether to drop a row or a column.
    """

    axis = classify_axis(axis)

    # Dropping a column
    if axis == 1:
        if label not in table.columns:
            raise ValueError(f"Column {label} does not exist in the DataFrame.")
        table.drop(labels=label, axis=axis, inplace=True)

    # Dropping a row
    else:
        label = int(label) - 1
        if label not in table.index:
            table.drop(labels=table.index[label], axis=axis, inplace=True)
        else:
            table.drop(labels=label, axis=axis, inplace=True)
    return table


def assign(table, row, column, value):
    """
    Assigns a value to a specific cell in the DataFrame.

    Parameters:
    - table: DataFrame in which the cell will be assigned.
    - row: The row index of the cell to be assigned.
    - column: The column index of the cell to be assigned.
    - value: The value to be assigned to the cell.
    """

    if row not in table.index:
        raise ValueError(f"Row {row} does not exist in the DataFrame.")
    if column not in table.columns:
        raise ValueError(f"Column {column} does not exist in the DataFrame.")

    table.at[row, column] = value

    return table


def copy(table, index, target_table, target_index, new_label=None, axis=0):
    """
    Copies a row or column from one DataFrame to another DataFrame.

    Parameters:
    - table: DataFrame from which the row/column will be copied.
    - index: The index of the row/column to be copied.
    - target_table: DataFrame to which the row/column will be copied.
    - target_index: The index at which the row/column will be copied in the target DataFrame.
    - axis: 0 for row, 1 for column. Specifies whether to copy a row or a column.
    """
    if axis == 1:
        # Copy column
        if target_index in target_table.columns:
            raise ValueError(f"Column {target_index} already exists in the target DataFrame.")
        column = table.iloc[:, index]
        target_table.insert(loc=target_index, column=new_label, value=column)
    else:
        # Copy row
        if target_index in target_table.index:
            raise ValueError(f"Row {target_index} already exists in the target DataFrame.")
        row = table.iloc[index]
        new_row = pd.DataFrame([row.values], columns=target_table.columns)
        target_table = pd.concat(
            [target_table.iloc[:target_index], new_row, target_table.iloc[target_index:]]
        ).reset_index(drop=True)

    return table, target_table


def merge(table, label_1, label_2, glue, new_label, axis=0):
    """
    Merges two rows or columns in a DataFrame into a new row or column, concatenating their contents with a specified glue string.

    Parameters:
    - table: DataFrame in which the rows/columns will be merged.
    - label_1, label_2: The labels of the rows/columns to be merged.
    - glue: String used to concatenate the contents of the rows/columns.
    - new_label: The label for the new merged row/column.
    - axis: 0 for merging rows, 1 for merging columns.
    """

    axis = classify_axis(axis)

    # Merging columns
    if axis == 1:
        if label_1 not in table.columns or label_2 not in table.columns:
            raise ValueError("One or both column labels do not exist in the DataFrame.")
        if new_label in table.columns:
            raise ValueError(f"Column {new_label} already exists in the DataFrame.")

        # Concatenate the columns with the specified glue and create a new column
        table[new_label] = (
            table[label_1].astype(str) + glue + table[label_2].astype(str)
        )

    # Merging rows
    else:
        label_1 = int(label_1) - 1
        label_2 = int(label_2) - 1
        new_label = int(new_label) - 1
        if label_1 not in table.index or label_2 not in table.index:
            raise ValueError("One or both row labels do not exist in the DataFrame.")
        if new_label in table.index:
            raise ValueError(f"Row {new_label} already exists in the DataFrame.")

        # Concatenate the rows with the specified glue and create a new row
        new_row = (
            table.loc[label_1].astype(str) + glue + table.loc[label_2].astype(str)
        ).rename(new_label)
        table.loc[new_label] = new_row.copy()

    return table


def split(table, label, delimiter, new_labels, axis=0):
    """
    Splits the contents of a row or column in the DataFrame into multiple new rows or columns.

    Parameters:
    - table: DataFrame in which the row/column will be split.
    - label: The label of the row/column to be split.
    - delimiter: The delimiter used to split the row/column content.
    - new_labels: List of new labels for the resulting split rows/columns.
    - axis: 0 for splitting a row, 1 for splitting a column.
    """

    axis = classify_axis(axis)

    # Splitting a column
    if axis == 1:
        if label not in table.columns:
            raise ValueError(f"Column {label} does not exist in the DataFrame.")

        # Perform the split operation and create new columns
        split_data = table[label].str.split(delimiter, expand=True)
        split_data.columns = new_labels

        # Drop the original column and add new columns
        table = table.drop(labels=label, axis=axis)
        table = pd.concat([table, split_data], axis=axis)

    # Splitting a row
    else:
        if label not in table.index:
            raise ValueError(f"Row {label} does not exist in the DataFrame.")

        # Perform the split operation and create new rows
        split_data = table.loc[label].str.split(delimiter).values[0]
        if len(split_data) != len(new_labels):
            raise ValueError(
                "The number of new labels must match the result of the split."
            )

        # Drop the original row and add new rows
        table = table.drop(labels=label, axis=axis)
        for new_label, data in zip(new_labels, split_data):
            table.loc[new_label] = data

    return table


def transpose(table):
    """
    Transposes the given DataFrame, swapping its rows and columns.

    Parameters:
    - table: DataFrame to be transposed.

    Returns:
    - A new DataFrame that is the transpose of the input DataFrame.
    """

    # Transpose the DataFrame
    transposed_table = table.transpose()

    return transposed_table


def aggregate(table, functions, axis=0):
    # Validate axis
    axis = classify_axis(axis)
    return table.agg(functions, axis=axis)


def test(table, label_1, label_2, strategy, axis=0):
    """
    Performs a specified statistical test between two rows or columns in the DataFrame.

    Parameters:
    - table: DataFrame on which the test will be performed.
    - label_1: The label of the first row/column to be tested.
    - label_2: The label of the second row/column to be tested.
    - strategy: The statistical test to perform ('t-test', 'z-test', 'chi-squared').
    - axis: 0 to test between columns, 1 to test between rows.
    """

    axis = classify_axis(axis)

    # Validate strategy
    supported_strategies = ["t-test", "z-test", "chi-squared"]
    if strategy not in supported_strategies:
        raise ValueError(
            f"Strategy '{strategy}' is not supported. Supported strategies are: {supported_strategies}"
        )

    # Perform the test between two columns
    if axis == 0:
        if label_1 not in table.columns or label_2 not in table.columns:
            raise ValueError(
                "One or both specified labels do not exist in the DataFrame's columns."
            )

        # Extract the data for each column
        data_1 = table[label_1]
        data_2 = table[label_2]

    # Perform the test between two rows
    else:
        if label_1 not in table.index or label_2 not in table.index:
            raise ValueError(
                "One or both specified labels do not exist in the DataFrame's index."
            )

        # Extract the data for each row
        data_1 = table.loc[label_1]
        data_2 = table.loc[label_2]

    # Perform a t-test
    if strategy == "t-test":
        test_stat, p_value = stats.ttest_ind(data_1, data_2)

    # Perform a z-test
    elif strategy == "z-test":
        z_stat, p_value = sm.stats.ztest(data_1, data_2)

    # Perform a chi-squared test
    elif strategy == "chi-squared":
        # For chi-squared test, we expect the data to be categorical and in a contingency table format
        # Here we construct a contingency table from the two data sets
        data_crosstab = pd.crosstab(data_1, data_2)
        chi2_stat, p_value, dof, expected = stats.chi2_contingency(data_crosstab)

        test_stat = chi2_stat

    # Create a new table to store the test results
    result_table = pd.DataFrame(index=range(2), columns=["Test Statistic", "P-Value"])
    result_table = assign(result_table, 1, 1, test_stat)
    result_table = assign(result_table, 1, 2, p_value)
    return result_table


def create_table(row_number, column_number):
    """
    Creates a new DataFrame with the specified number of rows and columns.

    Parameters:
    - row_number: The number of rows in the DataFrame.
    - column_number: The number of columns in the DataFrame.

    Returns:
    - A new DataFrame with the specified number of rows and columns.
    """

    # Create a new DataFrame with the specified dimensions
    new_table = pd.DataFrame(index=range(row_number), columns=range(column_number))

    return new_table
