import re
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm


def classify_axis(axis):
    """
    Converts the axis parameter to a numeric value if it is a string.
    """
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


def insert(table, index, index_name="new_column", axis=0):
    """
    Inserts an empty row or column at the specified index in the table.

    Parameters:
    - table: DataFrame in which the row/column will be inserted.
    - index: The index at which the row/column will be inserted.
    - index_name: The name of the new row/column.
    - axis:
      - 0 or "index": Indicates a row operation.
      - 1 or "columns": Indicates a column operation.
    """

    axis = classify_axis(axis)
    index = index - 1

    # Inserting a column
    if axis == 1:
        if index_name in table.columns:
            raise ValueError(f"Column {index_name} already exists in the DataFrame.")
        table.insert(loc=index, column=index_name, value=pd.Series([None] * len(table)))
    else:
        if index_name in table.index:
            raise ValueError(f"Row {index_name} already exists in the DataFrame.")
        new_row = pd.DataFrame([None] * len(table.columns)).T
        new_row.columns = table.columns
        new_row.index = [index_name]
        table = pd.concat(
            [table.iloc[:index], new_row, table.iloc[index:]]
        ).reset_index(drop=True)

    return table


def drop(table, label, axis=0):
    """
    Drops rows or columns in the table.

    Parameters:
    - table: DataFrame from which the row(s)/column(s) will be dropped.
    - label: The label(s) of the row(s)/column(s) to be dropped. For rows, this is the index label; for columns, this is the column name. It can be a single label or a list of labels.
    - axis:
      - 0 or "index": Indicates a row operation.
      - 1 or "columns": Indicates a column operation.
    """

    axis = classify_axis(axis)

    # Ensure label is a list
    if not isinstance(label, list):
        label = [label]

    # Dropping columns
    if axis == 1:
        missing_columns = [col for col in label if col not in table.columns]
        if missing_columns:
            raise ValueError(
                f"Column(s) {missing_columns} do not exist in the DataFrame."
            )
        table.drop(labels=label, axis=axis, inplace=True)

    # Dropping rows
    else:
        label = [str(int(l) - 1) for l in label]
        missing_rows = [l for l in label if l not in table.index]
        print(table.index)
        if missing_rows:
            raise ValueError(
                f"Row index(es) {missing_rows} do not exist in the DataFrame."
            )
        table.drop(labels=label, axis=axis, inplace=True)

    return table


def assign(
    table, start_row_index, end_row_index, start_column_index, end_column_index, values
):
    """
    Assigns a value to specific cells in the table.

    Parameters:
    - table: DataFrame in which the value will be assigned.
    - start_row_index, end_row_index: The range of row indices to assign the value to.
    - start_column_index, end_column_index: The range of column indices to assign the value to.
    - values: The value(s) to assign to the specified cell(s). Can be a single int/float/str or a list of lists of int/float/str.
    """
    # Adjust indices to be zero-based
    start_row_index -= 1
    end_row_index -= 1
    start_column_index -= 1
    end_column_index -= 1

    # If values is a single number, create a matrix of that value
    if isinstance(values, (int, float, str)):
        num_rows = end_row_index - start_row_index + 1
        num_columns = end_column_index - start_column_index + 1
        values = [[values] * num_columns] * num_rows

    # Assign the value(s) to the specified cell(s)
    table.iloc[
        start_row_index : end_row_index + 1, start_column_index : end_column_index + 1
    ] = values

    return table


def move(origin_table, origin_index, target_table, target_index, axis=0):
    """
    Moves a row or column from the origin table to the target table.

    Parameters:
    - origin_table: DataFrame from which the row/column will be moved.
    - origin_index: The index of the row/column to be moved.
    - target_table: DataFrame to which the row/column will be moved.
    - target_index: The index at which the row/column will be moved in the target DataFrame.
    - axis:
      - 0 or "index": Indicates a row operation.
      - 1 or "columns": Indicates a column operation.
    """

    axis = classify_axis(axis)
    origin_index -= 1
    target_index -= 1

    if axis == 0:  # Move row
        row = origin_table.iloc[origin_index]
        origin_table = origin_table.drop(origin_table.index[origin_index])
        target_table = pd.concat(
            [
                target_table.iloc[:target_index],
                row.to_frame().T,
                target_table.iloc[target_index:],
            ]
        ).reset_index(drop=True)
    elif axis == 1:  # Move column
        col = origin_table.iloc[:, origin_index]
        origin_table = origin_table.drop(origin_table.columns[origin_index], axis=1)
        target_table = pd.concat(
            [
                target_table.iloc[:, :target_index],
                col.to_frame(),
                target_table.iloc[:, target_index:],
            ],
            axis=1,
        )

    return origin_table, target_table


def copy(
    origin_table,
    origin_index,
    target_table,
    target_index,
    target_label_name=None,
    axis=0,
):
    """
    Copies a row or column from the origin table to the target table at the specified index.

    Parameters:
    - origin_table: DataFrame from which the row/column will be copied.
    - origin_index: The index of the row/column to be copied.
    - target_table: DataFrame to which the row/column will be copied.
    - target_index: The index at which the row/column will be copied in the target DataFrame.
    - target_label_name: The name of the new row/column in the target DataFrame.
    - axis:
      - 0 or "index": Indicates a row operation.
      - 1 or "columns": Indicates a column operation.
    """

    axis = classify_axis(axis)
    origin_index -= 1
    target_index -= 1

    if axis == 0:  # Copy row
        row = origin_table.iloc[origin_index]
        if target_label_name is not None:
            row.name = target_label_name
        else:
            row.name = target_index
        target_table = pd.concat(
            [
                target_table.iloc[:target_index],
                row.to_frame().T,
                target_table.iloc[target_index:],
            ]
        ).reset_index(drop=True)
    elif axis == 1:  # Copy column
        col = origin_table.iloc[:, origin_index]
        if target_label_name is not None:
            col.name = target_label_name
        else:
            col.name = target_index
        target_table = pd.concat(
            [
                target_table.iloc[:, :target_index],
                col.to_frame(),
                target_table.iloc[:, target_index:],
            ],
            axis=1,
        )

    return origin_table, target_table


def swap(table_a, label_a, table_b, label_b, axis=0):
    """
    Swaps rows or columns between two tables.

    Parameters:
    - table_a: The first DataFrame from which the row/column will be swapped.
    - label_a: The label of the row/column to be swapped in the first DataFrame.
    - table_b: The second DataFrame from which the row/column will be swapped.
    - label_b: The label of the row/column to be swapped in the second DataFrame.
    - axis:
      - 0 or "index": Indicates a row operation.
      - 1 or "columns": Indicates a column operation.
    """

    axis = classify_axis(axis)

    # Swapping columns
    if axis == 1:
        if label_a not in table_a.columns or label_b not in table_b.columns:
            raise ValueError(
                "One or both specified column labels do not exist in the respective DataFrames."
            )

        # Use temporary column names to avoid duplicates
        temp_label_a = "__temp__" + label_a
        temp_label_b = "__temp__" + label_b

        table_a.rename(columns={label_a: temp_label_a}, inplace=True)
        table_b.rename(columns={label_b: temp_label_b}, inplace=True)

        # Swap the columns
        table_a[temp_label_a], table_b[temp_label_b] = (
            table_b[temp_label_b],
            table_a[temp_label_a],
        )

        table_a.rename(columns={temp_label_a: label_b}, inplace=True)
        table_b.rename(columns={temp_label_b: label_a}, inplace=True)

    # Swapping rows
    else:
        label_a = int(label_a) - 1
        label_b = int(label_b) - 1

        if label_a not in table_a.index or label_b not in table_b.index:
            raise ValueError(
                "One or both specified row labels do not exist in the respective DataFrames."
            )

        # Swap the rows between the two DataFrames
        temp_row_a = table_a.loc[label_a].copy()
        table_a.loc[label_a] = table_b.loc[label_b]
        table_b.loc[label_b] = temp_row_a

    return table_a, table_b


def merge(table_a, table_b, how="outer", on=None, axis=0):
    """
    Merges two tables based on a common column or along columns.

    Parameters:
    - table_a: First table
    - table_b: Second table
    - how: Type of merge to be performed. Options are 'left', 'right', 'outer', 'inner'. Default is 'outer'.
    - on: Column or index level names to join on. Must be found in both DataFrames. If not provided and the DataFrames
          have a common column, will default to the intersection of the columns in the DataFrames.
    - axis: Axis to concatenate along. 0 or "index" for row-wise, 1 or "column" for column-wise. Default is 0.
    """

    axis = classify_axis(axis)

    if axis == 0:
        return pd.concat([table_a, table_b], ignore_index=True)
    elif axis == 1:
        return pd.merge(table_a, table_b, how=how, on=on)

    return result


def concatenate(table, label_a, label_b, glue, new_label, axis=0):
    """
    Concatenates two labels and appends the merged label to the table.

    Parameters:
    - table: DataFrame in which the rows/columns will be concatenated.
    - label_a: The label of the first row/column to be concatenated.
    - label_b: The label of the second row/column to be concatenated.
    - glue: The string to be used to concatenate the two rows/columns.
    - new_label: The label of the new row/column created by the concatenation.
    - axis:
      - 0 or "index": Indicates a row operation.
      - 1 or "columns": Indicates a column operation.
    """

    axis = classify_axis(axis)

    # Merging columns
    if axis == 1:
        if label_a not in table.columns or label_b not in table.columns:
            raise ValueError("One or both column labels do not exist in the DataFrame.")
        if new_label in table.columns:
            raise ValueError(f"Column {new_label} already exists in the DataFrame.")

        # Concatenate the columns with the specified glue and create a new column
        table[new_label] = (
            table[label_a].astype(str) + glue + table[label_b].astype(str)
        )

    # Merging rows
    else:
        label_a = int(label_a) - 1
        label_b = int(label_b) - 1
        new_label = int(new_label) - 1
        if label_a not in table.index or label_b not in table.index:
            raise ValueError("One or both row labels do not exist in the DataFrame.")
        if new_label in table.index:
            raise ValueError(f"Row {new_label} already exists in the DataFrame.")

        # Concatenate the rows with the specified glue and create a new row
        new_row = (
            table.loc[label_a].astype(str) + glue + table.loc[label_b].astype(str)
        ).rename(new_label)
        table.loc[new_label] = new_row.copy()

    return table


def split(table, label, delimiter, new_labels, axis=0):
    """
    Splits a label into multiple parts at each occurrence of the specified delimiter.

    Parameters:
    - table: DataFrame in which the row/column will be split.
    - label: The label of the row/column to be split.
    - delimiter: The delimiter used to split the row/column content.
    - new_labels: List of new labels for the resulting split rows/columns.
    - axis:
      - 0 or "index": Indicates a row operation.
      - 1 or "columns": Indicates a column operation.
    """

    axis = classify_axis(axis)

    # Splitting a column
    if axis == 1:
        if label not in table.columns:
            raise ValueError(f"Column {label} does not exist in the DataFrame.")

        # Perform the split operation and create new columns
        split_data = (
            table[label].str.split(delimiter).apply(lambda x: [i for i in x if i])
        )
        split_data = pd.DataFrame(split_data.tolist(), index=table.index)
        if len(split_data.columns) != len(new_labels):
            raise ValueError(
                "The number of new labels must match the number of split parts."
            )
        split_data.columns = new_labels

        # Drop the original column and add new columns
        table = table.drop(labels=label, axis=axis)
        table = pd.concat([table, split_data], axis=axis)

    # Splitting a row
    else:
        if label not in table.index:
            raise ValueError(f"Row {label} does not exist in the DataFrame.")

        # Perform the split operation and create new rows
        split_data = [i for i in table.loc[label].split(delimiter) if i]
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
    Transposes the given table.

    Parameters:
    - table: DataFrame to be transposed.
    """

    # Transpose the DataFrame
    transposed_table = table.transpose()

    return transposed_table


def aggregate(table, functions, axis=0):
    """
    Aggregates the table using the specified function.

    Parameters:
    - table: DataFrame to be aggregated.
    - functions: A function or list of functions to apply to each column/row.
    - axis:
      - 0 or "index": Indicates a row operation.
      - 1 or "columns": Indicates a column operation.
    """

    axis = classify_axis(axis)
    if axis == 0:
        axis = 1
    elif axis == 1:
        axis = 0

    try:
        result = table.agg(functions, axis=axis)
        if isinstance(result, pd.Series):
            result = result.to_frame().transpose() if axis == 0 else result.to_frame()
    except Exception as e:
        raise ValueError(f"Error applying aggregation functions: {e}")

    return result


def test(table, label_a, label_b, strategy, axis=0):
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

    axis = classify_axis(axis)

    # Validate strategy
    supported_strategies = ["t-test", "z-test", "chi-squared"]
    if strategy not in supported_strategies:
        raise ValueError(
            f"Strategy '{strategy}' is not supported. Supported strategies are: {supported_strategies}"
        )

    # Perform the test between two columns
    if axis == 0:
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

    # Perform a chi-squared test
    elif strategy == "chi-squared":
        # For chi-squared test, we expect the data to be categorical and in a contingency table format
        # Here we construct a contingency table from the two data sets
        data_crosstab = pd.crosstab(data_1, data_2)
        chi2_stat, p_value, dof, expected = stats.chi2_contingency(data_crosstab)

        test_stat = chi2_stat

    # Create a new table to store the test results
    result_table = pd.DataFrame(index=range(1), columns=["Test Statistic", "P-Value"])
    result_table = assign(result_table, 1, 1, 1, 1, test_stat)
    result_table = assign(result_table, 1, 1, 2, 2, p_value)
    return result_table


def rearrange(table, by_values=None, by_array=None, axis=0):
    """
    Rearranges the rows or columns of the table based on the specified order.

    Parameters:
    - table: DataFrame to be rearranged.
    - by_values: If this parameter is set, the rows/columns will be rearranged based on the values in the specified row/column.
    - by_array: If this parameter is set, the rows/columns will be rearranged based on the order of the values in the array.
    - axis:
        - 0 or "index": Indicates a row operation.
        - 1 or "columns": Indicates a column operation.
    """

    axis = classify_axis(axis)
    print(by_values)
    print(axis)
    if by_values is not None:
        if axis == 0:
            sorted_indices = table[by_values].argsort()
            return table.iloc[sorted_indices]
        elif axis == 1:

            sorted_indices = table.loc[by_values].argsort()
            return table.iloc[:, sorted_indices]
        else:
            raise ValueError(
                "axis should be 0 or 'index' for row operation, 1 or 'columns' for column operation"
            )
    elif by_array is not None:
        if axis == 0:
            return table.iloc[by_array]
        elif axis == 1:
            return table.iloc[:, by_array]
        else:
            raise ValueError(
                "axis should be 0 or 'index' for row operation, 1 or 'columns' for column operation"
            )
    else:
        raise ValueError("Either by_values or by_array must be provided")

    return table


def format(table, label, pattern, replace_with="", axis=0):
    """
    Formats the values in a row or column based on the specified pattern.

    Parameters:
    - table: DataFrame in which the row/column will be formatted.
    - label: The label of the row/column to be formatted.
    - pattern: The format regex pattern to apply to the values.
    - replace_with: The string to replace the matched pattern with.
    - axis: 0 or "index" for a row operation, 1 or "columns" for a column operation.
    """

    axis = classify_axis(axis)

    # Format the values in a column
    if axis == 1:
        if label not in table.columns:
            raise ValueError(f"Column {label} does not exist in the DataFrame.")

        # Apply the format pattern to the column values
        table[label] = table[label].apply(
            lambda x: re.sub(pattern, replace_with, str(x))
        )

    # Format the values in a row
    else:
        if label not in table.index:
            raise ValueError(f"Row {label} does not exist in the DataFrame.")

        # Apply the format pattern to the row values
        table.loc[label] = table.loc[label].apply(
            lambda x: re.sub(pattern, replace_with, str(x))
        )

    return table


def divide(table, by_values=None, by_array=None, axis=0):
    """
    Divides the table by the specific values of a row or column or by the given sets of rows or columns.

    Parameters:
    - table (str): table to be divided.
    - by_values (str): Column/Row name to group the table by.
    - by_array (list[list[str/int]]): List of lists of column/row indexes to group the table by.
    - axis (str or int):
        - 0 or "index": Indicates to divide the table by a row.
        - 1 or "columns": Indicates to divide the table by a column.
    """
    axis = classify_axis(axis)

    if by_values:
        if axis == 1:
            groups = table.groupby(by)
        elif axis == 0:
            groups = table.T.groupby(by).T

        result = []
        for group in groups:
            result.append(
                {
                    "unique_value": group[0],
                    "data": group[1].reset_index(drop=True),
                }
            )
        return result
    
    elif by_array:
        result = []
        if axis == 1:
            for index, group in enumerate(by_array, start=1):
                subset = table[group]
                result.append({
                    "unique_value": f"table {index}",
                    "data": subset.reset_index(drop=True)
                })
        elif axis == 0:
            for index, group in enumerate(by_array, start=1):
                subset = table.iloc[group]
                result.append({
                    "unique_value": f"table {index}",
                    "data": subset.reset_index(drop=True)
                })
        return result

    else:
        raise ValueError("Either by_values or by_array must be provided.")


def pivot_table(table, index, columns, values, aggfunc="first"):
    """
    Reshapes the table based on the specified index, columns, values, and aggregation function.

    Parameters:
    - table (DataFrame): The table to pivot.
    - index (str): The column name to use as the new row headers.
    - columns (str): The column name to use as the new column headers.
    - values (str): The column name whose values will fill the new table.
    - aggfunc (str): The aggregation function to apply to the values. Common options are 'first', 'sum', 'mean', etc.

    Returns:
    DataFrame: The pivoted table.
    """
    pivot_df = table.pivot_table(
        index=index, columns=columns, values=values, aggfunc=aggfunc
    ).reset_index()
    return pivot_df


def fill(table, method, column=None):
    """
    Fills missing values in the table using the specified method.

    Parameters:
    - table: Table to fill missing values.
    - method: The method to use for filling missing values. Choose from 'value', 'mean', 'median', 'mode', 'ffill', 'bfill', 'interpolate'.
    - column: The column to fill missing values in. If None, missing values in all columns will be filled.
    """
    df = table.copy()
    if not isinstance(column, list):
        columns = [column]
    else:
        columns = None

    if method == "mean":
        if columns:
            for column in columns:
                df[column].fillna(df[column].mean(), inplace=True)
        else:
            for col in df.columns:
                if df[col].dtype != "O":  # Skip non-numeric columns
                    df[col].fillna(df[col].mean(), inplace=True)
    elif method == "median":
        if columns:
            for column in columns:
                df[column].fillna(df[column].median(), inplace=True)
        else:
            for col in df.columns:
                if df[col].dtype != "O":  # Skip non-numeric columns
                    df[col].fillna(df[col].median(), inplace=True)
    elif method == "mode":
        if columns:
            for column in columns:
                df[column].fillna(df[column].mode()[0], inplace=True)
        else:
            for col in df.columns:
                df[col].fillna(df[col].mode()[0], inplace=True)
    elif method in ["ffill", "bfill"]:
        if columns:
            for column in columns:
                df[column].fillna(method=method, inplace=True)
        else:
            df.fillna(method=method, inplace=True)
    elif method == "interpolate":
        if columns:
            for column in columns:
                df[column].interpolate(inplace=True)
        else:
            df.interpolate(inplace=True)
    else:
        raise ValueError(
            "Invalid method. Choose from 'value', 'mean', 'median', 'mode', 'ffill', 'bfill', 'interpolate'."
        )

    return df
