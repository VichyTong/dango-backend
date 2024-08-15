from functions import DangoFunction

class DangoFill(DangoFunction):
    def __init__(self):
        super().__init__(function_type="A")

    def execute(self, table, method, column):
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