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


def aggregate(table, functions, axis=0):
    axis = classify_axis(axis)
    # Warn: Special change for better LLM understanding, please refer to the definition.
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


def assign(
    table, start_row_index, end_row_index, start_column_index, end_column_index, values
):
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

    table.iloc[
        start_row_index : end_row_index + 1, start_column_index : end_column_index + 1
    ] = values

    return table


def blank_table(num_rows, num_columns):
    return pd.DataFrame(index=range(num_rows), columns=range(num_columns))


def concatenate(table, label_a, label_b, glue, new_label, axis=0):
    axis = classify_axis(axis)

    # Merging columns
    if axis == 1:
        if label_a not in table.columns or label_b not in table.columns:
            raise ValueError("One or both column labels do not exist in the DataFrame.")
        if new_label in table.columns:
            raise ValueError(f"Column {new_label} already exists in the DataFrame.")
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
        new_row = (
            table.loc[label_a].astype(str) + glue + table.loc[label_b].astype(str)
        ).rename(new_label)
        table.loc[new_label] = new_row.copy()

    return table


def copy(
    origin_table,
    origin_index,
    target_table,
    target_index,
    target_label_name=None,
    axis=0,
):
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

    return target_table


def divide(table, by, axis=0):
    axis = classify_axis(axis)

    if axis == 1:
        groups = table.groupby(by)
    elif axis == 0:
        groups = table.T.groupby(by).T

    result = []
    for group in groups:
        result.append(group[1].reset_index(drop=True))
    return result


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
    if not isinstance(label, list):
        label = [label]

    if axis == 1:
        missing_columns = [col for col in label if col not in table.columns]
        if missing_columns:
            raise ValueError(
                f"Column(s) {missing_columns} do not exist in the DataFrame."
            )
        table.drop(labels=label, axis=axis, inplace=True)
    else:
        if isinstance(label[0], int):
            label = [str(l + 1) for l in label]
        missing_rows = [l for l in label if l not in table.index]
        if missing_rows:
            raise ValueError(
                f"Row index(es) {missing_rows} do not exist in the DataFrame."
            )
        table.drop(labels=label, axis=axis, inplace=True)

    return table


def fill(table, method, column=None):
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


def format(table, label, pattern, replace_with="", axis=0):
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


def insert(table, index, index_name="new_column", axis=0):
    axis = classify_axis(axis)

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


def merge(table_a, table_b, how="outer", on=None, axis=0):
    axis = classify_axis(axis)

    if axis == 0:
        return pd.concat([table_a, table_b], ignore_index=True)
    elif axis == 1:
        return pd.merge(table_a, table_b, how=how, on=on)


def move(origin_table, origin_index, target_table, target_index, axis=0):
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


def pivot_table(table, index, columns, values, aggfunc="first"):
    pivot_df = table.pivot_table(
        index=index, columns=columns, values=values, aggfunc=aggfunc
    ).reset_index()
    return pivot_df


def rearrange(table, by_values=None, by_array=None, axis=0):
    axis = classify_axis(axis)
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


def split(table, label, delimiter, new_label_list, axis=0):
    axis = classify_axis(axis)

    def split_rows(df, label, delimiter, new_label_list):
        new_rows = []
        for _, row in df.iterrows():
            split_values = row[label].split(delimiter)
            for i, value in enumerate(split_values):
                new_row = row.copy()
                if new_label_list and i < len(new_label_list):
                    new_row[new_label_list[i]] = value.strip()
                else:
                    new_row[label] = value.strip()
                new_rows.append(new_row)
        return pd.DataFrame(new_rows)


    def split_columns(df, label, delimiter, new_label_list):
        new_columns = df[label].str.split(delimiter, expand=True)
        if new_label_list and len(new_label_list) == new_columns.shape[1]:
            new_columns.columns = new_label_list
        else:
            new_columns.columns = [
                f"{label}_part{i+1}" for i in range(new_columns.shape[1])
            ]
        df = df.drop(columns=[label])
        df = pd.concat([df, new_columns], axis=1)
        return df

    if axis == 0:
        return split_rows(table, label, delimiter)
    elif axis == 1:
        return split_columns(table, label, delimiter, new_label_list)
    else:
        raise ValueError("Invalid axis. Use 0 for rows or 1 for columns.")


def subtable(table, row_list, column_list):
    if row_list is None:
        row_list = table.index.tolist()
    if column_list is None:
        column_list = table.columns.tolist()

    return table.loc[row_list, column_list]


def swap(table_a, label_a, table_b, label_b, axis=0):
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


def test(table_a, label_a, table_b, label_b, strategy, axis=0):
    axis = classify_axis(axis)

    # Validate strategy
    supported_strategies = ["t-test", "z-test", "chi-squared", "pearson-correlation"]
    if strategy not in supported_strategies:
        raise ValueError(
            f"Strategy '{strategy}' is not supported. Supported strategies are: {supported_strategies}"
        )

    # Perform the test between two columns
    if axis == 1:
        if label_a not in table_a.columns or label_b not in table_b.columns:
            raise ValueError(
                "One or both specified labels do not exist in the DataFrame's columns."
            )

        # Extract the data for each column
        data_1 = table_a[label_a]
        data_2 = table_b[label_b]

    # Perform the test between two rows
    else:
        if label_a not in table_a.index or label_b not in table_b.index:
            raise ValueError(
                "One or both specified labels do not exist in the DataFrame's index."
            )

        # Extract the data for each row
        data_1 = table_a.loc[label_a]
        data_2 = table_b.loc[label_b]

    # Perform a t-test
    if strategy == "t-test":
        test_stat, p_value = stats.ttest_ind(data_1, data_2)

    # Perform a z-test
    elif strategy == "z-test":
        test_stat, p_value = sm.stats.ztest(data_1, data_2)

    # Perform a chi-squared test
    elif strategy == "chi-squared":
        # For chi-squared test, we expect the data to be categorical and in a contingency table format
        # Here we construct a contingency table from the two data sets
        data_crosstab = pd.crosstab(data_1, data_2)
        chi2_stat, p_value, dof, expected = stats.chi2_contingency(data_crosstab)

        test_stat = chi2_stat

    elif strategy == "pearson-correlation":
        test_stat, p_value = stats.pearsonr(data_1, data_2)
    
    return test_stat, p_value


def transpose(table):
    # Transpose the DataFrame
    transposed_table = table.transpose()

    return transposed_table
