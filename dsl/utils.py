import re
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from thefuzz import process

pd.set_option("future.no_silent_downcasting", True)


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
        if isinstance(label_a, int):
            label_a = str(label_a + 1)
        if isinstance(label_b, int):
            label_b = str(label_b + 1)
        if isinstance(new_label, int):
            new_label = str(new_label + 1)

        if label_a not in table.index or label_b not in table.index:
            raise ValueError("One or both row labels do not exist in the DataFrame.")
        if new_label in table.index:
            raise ValueError(f"Row {new_label} already exists in the DataFrame.")
        new_row = (
            table.loc[label_a].astype(str) + glue + table.loc[label_b].astype(str)
        ).rename(new_label)
        table.loc[new_label] = new_row.copy()

    return table


def copy(origin_table, origin_label, target_table, target_label, axis):
    axis = classify_axis(axis)

    if axis == 1:  # Copying columns
        if isinstance(origin_label, int):
            origin_label = origin_table.columns[origin_label]
        if isinstance(target_label, int):
            target_label = target_table.columns[target_label]

        if isinstance(origin_label, str) and isinstance(target_label, str):
            target_table[target_label] = origin_table[origin_label]

            # Update the column name and maintain order
            columns = list(target_table.columns)
            origin_index = columns.index(target_label)
            columns[origin_index] = target_label
            target_table = target_table[columns]
            target_table.rename(columns={target_label: origin_label}, inplace=True)

        else:
            raise ValueError("Invalid column labels.")

    elif axis == 0:  # Copying rows
        if isinstance(origin_label, int):
            origin_label = str(origin_label + 1)

        if isinstance(origin_label, int) or isinstance(origin_label, str):
            row_data = origin_table.loc[origin_label]

            if target_label in target_table.index:
                target_table.drop(index=target_label, inplace=True)

            target_table.loc[target_label] = row_data
            # Reorder rows to preserve the original order
            rows = list(target_table.index)
            rows.remove(target_label)
            rows.insert(rows.index(origin_label), target_label)
            target_table = target_table.reindex(rows)

        else:
            raise ValueError("For axis=0, origin_label must be an int or str.")

    else:
        raise ValueError("Invalid axis. Use 0 for rows or 1 for columns.")

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
    axis = classify_axis(axis)
    if not isinstance(label, list):
        label = [label]

    if axis == 1:  # Dropping columns
        valid_columns = [col for col in label if col in table.columns]
        if valid_columns:
            table.drop(labels=valid_columns, axis=axis, inplace=True)
    else:  # Dropping rows
        if isinstance(label[0], int):
            label = [str(l + 1) for l in label]
        valid_rows = [l for l in label if l in table.index]
        if valid_rows:
            table.drop(labels=valid_rows, axis=axis, inplace=True)

    return table


def fill(table, labels, method, axis=0):
    axis = classify_axis(axis)
    df = table.copy()
    df.replace("", None, inplace=True)
    if isinstance(labels, (int, str)):
        labels = [labels]

    def should_skip(series):
        """Check if the first value of the series is a string."""
        return isinstance(series.iloc[0], str)

    if axis == 0:
        for label in labels:
            # Adjust label if it's an integer (assuming labels are strings)
            if isinstance(label, int):
                label = str(label + 1)

            if label not in df.index:
                continue  # Skip if label does not exist

            series = df.loc[label]
            if should_skip(series):
                series_slice = series.iloc[1:]
                filled_series = series_slice.fillna(
                    series_slice.mean()
                    if method == "mean"
                    else (
                        series_slice.median()
                        if method == "median"
                        else (
                            series_slice.mode()[0]
                            if method == "mode"
                            else (
                                series_slice.fillna(method=method)
                                if method in ["ffill", "bfill"]
                                else (
                                    series_slice.interpolate()
                                    if method == "interpolate"
                                    else series_slice
                                )
                            )
                        )
                    )  # No action if the method is not recognized
                )
                filled_series = filled_series.infer_objects(copy=False)
                df.loc[label, series.index[1:]] = filled_series
            else:
                df.loc[label] = series.fillna(
                    series.mean()
                    if method == "mean"
                    else (
                        series.median()
                        if method == "median"
                        else (
                            series.mode()[0]
                            if method == "mode"
                            else (
                                series.fillna(method=method)
                                if method in ["ffill", "bfill"]
                                else (
                                    series.interpolate()
                                    if method == "interpolate"
                                    else series
                                )
                            )
                        )
                    )  # No action if the method is not recognized
                )
    elif axis == 1:
        for label in labels:
            if isinstance(label, int):
                label = df.columns[label]

            series = df[label]
            if should_skip(series):
                series_slice = series.iloc[1:]
                filled_series = series_slice.fillna(
                    series_slice.mean()
                    if method == "mean"
                    else (
                        series_slice.median()
                        if method == "median"
                        else (
                            series_slice.mode()[0]
                            if method == "mode"
                            else (
                                series_slice.fillna(method=method)
                                if method in ["ffill", "bfill"]
                                else (
                                    series_slice.interpolate()
                                    if method == "interpolate"
                                    else series_slice
                                )
                            )
                        )
                    )  # No action if the method is not recognized
                )
                filled_series = filled_series.infer_objects(copy=False)
                df.loc[series.index[1:], label] = filled_series
            else:
                df[label] = series.fillna(
                    series.mean()
                    if method == "mean"
                    else (
                        series.median()
                        if method == "median"
                        else (
                            series.mode()[0]
                            if method == "mode"
                            else (
                                series.fillna(method=method)
                                if method in ["ffill", "bfill"]
                                else (
                                    series.interpolate()
                                    if method == "interpolate"
                                    else series
                                )
                            )
                        )
                    )  # No action if the method is not recognized
                )
    else:
        raise ValueError("Invalid axis. Use 0 for rows or 1 for columns.")

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
        if isinstance(label, int):
            label = str(label + 1)
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


def merge(table_a, table_b, how="outer", on=None):
    if how == "fuzzy":

        def find_best_match(name, names, threshold=70):
            match, score = process.extractOne(name, names)
            return match if score >= threshold else None

        table_a["matched_name"] = table_a[on].apply(
            find_best_match, names=table_b[on].to_list()
        )
        merged_df = pd.merge(table_a, table_b, left_on="matched_name", right_on=on)
        merged_df = merged_df.drop(columns=["matched_name", f"{on}_y"]).rename(
            columns={f"{on}_x": on}
        )
        return merged_df
    else:
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


def split(table, label, delimiter, new_label_list=None, axis=0):
    axis = classify_axis(axis)

    def split_rows(df, label, delimiter):
        new_rows = []
        for _, row in df.iterrows():
            split_values = row[label].split(delimiter)
            for i, value in enumerate(split_values):
                new_row = row.copy()
                new_row[label] = value.strip()
                new_rows.append(new_row)

        # Create the new DataFrame and reset the index
        new_df = pd.DataFrame(new_rows)
        return new_df.reset_index(drop=True)

    def split_columns(df, label, delimiter, new_label_list):
        new_columns = df[label].str.split(delimiter, expand=True)
        if new_label_list and len(new_label_list) == new_columns.shape[1]:
            new_columns.columns = new_label_list
        else:
            new_columns.columns = [
                f"{label}_part{i+1}" for i in range(new_columns.shape[1])
            ]

        column_position = df.columns.get_loc(label)
        df = df.drop(columns=[label])
        for i, col in enumerate(new_columns.columns):
            df.insert(column_position + i, col, new_columns[col])
        return df

    if axis == 0:
        return split_rows(table, label, delimiter, new_label_list)
    elif axis == 1:
        return split_columns(table, label, delimiter, new_label_list)
    else:
        raise ValueError("Invalid axis. Use 0 for rows or 1 for columns.")


def subtable(table, labels, axis=0):
    axis = classify_axis(axis)
    if not isinstance(labels, list):
        labels = [labels]

    if axis == 1:
        if isinstance(labels[0], int):
            labels = [table.columns[l] for l in labels]
        return table[labels]
    else:
        if isinstance(labels[0], int):
            labels = [str(l + 1) for l in labels]
        return table.loc[labels]


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
        if isinstance(label_a, int):
            label_a = str(label_a + 1)
        if isinstance(label_b, int):
            label_b = str(label_b + 1)

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
        if isinstance(label_a, int):
            label_a = str(label_a + 1)
        if isinstance(label_b, int):
            label_b = str(label_b + 1)

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
