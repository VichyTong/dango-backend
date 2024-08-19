from pydantic import BaseModel, ValidationError
from typing import List, Union, Optional


class FunctionCall(BaseModel):
    function_name: str
    arguments: List


def create_error_message(error, error_message, function_name=None):

    if function_name:
        return {
            "error_type": error,
            "function_name": function_name,
            "error_message": error_message
        }
    else:
        return {
            "error_type": error,
            "error_message": error_message
        }


def validate_dsls_format(function_calls: List[dict], error_list=[]):
    try:
        validated_calls = [FunctionCall(**call) for call in function_calls]
        return validated_calls
    except ValidationError as e:
        error = create_error_message("DSLs format is invalid", "The format should be a list of dictionaries with keys 'function_name' and 'arguments' where 'arguments' is a list.")
        error_list.append(error)
        return "Failed"


# blank_table(row_number, column_number): Returns a empty table with the specified number of rows and columns.
# Parameters:
# - row_number (int, required): The number of rows in the table.
# - column_number (int, required): The number of columns in the table.
# Output:
# - A pandas DataFrame.

class BLANK_TABLE_PARAMS(BaseModel):
    row_number: int
    column_number: int

def blank_table(params: BLANK_TABLE_PARAMS):
    return

# delete_table(table_name): Deletes the specified table.
# Parameters:
# - table_name (str): The name of the table to be deleted.

class DELETE_TABLE_PARAMS(BaseModel):
    table_name: str


def delete_table(params: DELETE_TABLE_PARAMS):
    return

# insert(table_name, index, index_name, axis): Inserts an empty row or column at the specified index in the table.
# Parameters:
# - table_name (str): The name of the table to insert the row/column into.
# - index (int): The index at which the row/column will be inserted.
# - index_name (str): The name of the new row/column.
# - axis (str or int): Refers to the direction of the operation.


class INSERT_PARAMS(BaseModel):
    table_name: str
    index: int
    index_name: str
    axis: Union[str, int]


def insert(params: INSERT_PARAMS):
    return

# drop(table_name, label, axis): Drops a row or column in the table.
# Parameters:
# - table_name (str): The name of the table to drop the row/column from.
# - label (str or int or list[str] or list[int]): The label or list of labels of the row/column to be dropped.
# - axis (str or int): Refers to the direction of the operation.


class DROP_PARAMS(BaseModel):
    table_name: str
    label: Union[str, int, List[str], List[int]]
    axis: Union[str, int]


def drop(params: DROP_PARAMS):
    return

# assign(table_name, start_row_index, end_row_index, start_column_index, end_column_index, values): Assigns a value to specific cells in the table.
# Parameters:
# - table_name (str): The name of the table to assign the value to.
# - start_row_index, end_row_index (int): The range of row indices to assign the value to.
# - start_column_index, end_column_index (int): The range of column indices to assign the value to.
# - values (list[list[int/float/str]] or int/float/str): The value(s) to assign to the specified cell(s). Can be a single int/float/str or a list of lists of int/float/str.


class ASSIGN_PARAMS(BaseModel):
    table_name: str
    start_row_index: int
    end_row_index: int
    start_column_index: int
    end_column_index: int
    values: Union[List[List[int]], int]


def assign(params: ASSIGN_PARAMS):
    return

# move(origin_table_name, origin_index, target_table_name, target_index, axis): Moves a row or column from the origin table to the target table.
# Parameters:
# - origin_table_name (str): The name of the table from which the row/column will be moved.
# - origin_index (int): The index of the row/column to be moved.
# - target_table_name (str): The name of the table to which the row/column will be moved.
# - target_index (int): The index at which the row/column will be moved in the target table.
# - axis (str or int): Refers to the direction of the operation.


class MOVE_PARAMS(BaseModel):
    origin_table_name: str
    origin_index: int
    target_table_name: str
    target_index: int
    axis: Union[str, int]


def move(params: MOVE_PARAMS):
    return

# copy(origin_table_name, origin_index, target_table_name, target_index, axis): Copies a row or column from the origin table to the target table at the specified index.
# Parameters:
# - origin_table_name (str): The name of the table from which the row/column will be copied.
# - origin_index (int): The index of the row/column to be copied.
# - target_table_name (str): The name of the table to which the row/column will be copied.
# - target_index (int): The index at which the row/column will be copied in the target table.
# - target_label_name (str): The name of the new row/column in the target table.
# - axis (str or int): Refers to the direction of the operation.


class COPY_PARAMS(BaseModel):
    origin_table_name: str
    origin_index: int
    target_table_name: str
    target_index: int
    target_label_name: str
    axis: Union[str, int]


def copy(params: COPY_PARAMS):
    return

# swap(table_name_a, label_a, table_name_b, label_b, axis): Swaps rows or columns between two tables.
# Parameters:
# - table_name_a (str): The first table from which the row/column will be swapped.
# - label_a (str or int): The label of the row/column to be swapped in the first table.
# - table_name_b (str): The second table from which the row/column will be swapped.
# - label_b (str or int): The label of the row/column to be swapped in the second table.
# - axis (str or int): Refers to the direction of the operation.


class SWAP_PARAMS(BaseModel):
    table_name_a: str
    label_a: Union[str, int]
    table_name_b: str
    label_b: Union[str, int]
    axis: Union[str, int]


def swap(params: SWAP_PARAMS):
    return

# merge(table_a, table_b, how="outer", on=None, axis=0): Merges two tables based on a common column or along columns.
# Parameters:
# - table_a: First table
# - table_b: Second table
# - how: Type of merge to be performed. Options are 'left', 'right', 'outer', 'inner'. Default is 'outer'.
# - on: Column or index level names to join on. Must be found in both DataFrames. If not provided and the DataFrames have a common column, will default to the intersection of the columns in the DataFrames.
# - axis: Axis to concatenate along. 0 or "index" for row-wise, 1 or "column" for column-wise. Default is 0.


class MERGE_PARAMS(BaseModel):
    table_name_a: str
    table_name_b: str
    how: str
    on: Optional[str]
    axis: Union[str, int]


def merge(params: MERGE_PARAMS):
    return

# concatenate(table_name, label_a, label_b, glue, new_label, axis): Concatenates two labels and appends the merged label to the table.
# Parameters:
# - table_name (str): table in which the rows/columns will be concatenated.
# - label_a (str or int): The label of the first row/column to be concatenated.
# - label_b (str or int): The label of the second row/column to be concatenated.
# - glue (str): The string to be used to concatenate the two rows/columns.
# - new_label (str or int): The label of the new row/column created by the concatenation.
# - axis (str or int): Refers to the direction of the operation.


class CONCATENATE_PARAMS(BaseModel):
    table_name: str
    label_a: Union[str, int]
    label_b: Union[str, int]
    glue: str
    new_label: Union[str, int]
    axis: Union[str, int]


def concatenate(params: CONCATENATE_PARAMS):
    return

# split(table, label, delimiter, axis, split_column=None): Splits rows or columns in the given table based on a specified delimiter.
# Parameters:
# - table_name (str): The table in which the rows/columns will be split.
# - label (str or int): The label of the row/column to be split.
# - delimiter (str): The delimiter to use for splitting the rows/columns.
# - axis (str or int):
#     - 0 or 'index' for row splitting
#     - 1 or 'columns' for column splitting.
# - split_column (list of str, optional): The label of the column to split when mode is 'columns'. Required for 'columns' mode.


class SPLIT_PARAMS(BaseModel):
    table_name: str
    label: Union[str, int]
    delimiter: str
    axis: Union[str, int]

def split(params: SPLIT_PARAMS):
    return

# transpose(table_name): Transposes the given table.
# Parameters:
# - table_name (str): table to be transposed.


class TRANSPOSE_PARAMS(BaseModel):
    table_name: str


def transpose(params: TRANSPOSE_PARAMS):
    return


# aggregate(table_name, functions, axis): Aggregates the table using the specified function.
# Parameters:
# - table_name (str): table to be aggregated.
# - functions (dict): Keys are names of rows or columns, and values are lists of function names. Example: {'A': ['sum', 'mean'], 'B': ['min', 'max']}.
# - axis (str or int): Refers to the direction of the operation.

class AGGREGATE_PARAMS(BaseModel):
    table_name: str
    functions: dict
    axis: Union[str, int]


def aggregate(params: AGGREGATE_PARAMS):
    return

# test(table_name, label_a, label_b, strategy, axis): Returns a new result table by comparing two labels using the specified strategy.
# Parameters:
# - table_name (str): table on which the test will be performed.
# - label_a (str or int): The label of the first row/column to be tested.
# - label_b (str or int): The label of the second row/column to be tested.
# - strategy (str): The stati   stical test to perform ('t-test', 'z-test', 'chi-squared').
# - axis (str or int): Refers to the direction of the operation.


class TEST_PARAMS(BaseModel):
    table_name_a: str
    label_a: Union[str, int]
    table_name_b: str
    label_b: Union[str, int]
    strategy: str
    axis: Union[str, int]


def test(params: TEST_PARAMS):
    return


# format(table_name, label, pattern, replace_with, axis): Formats the values in a row or column based on the specified pattern.
# Parameters:
# - table_name: table in which the row/column will be formatted.
# - label: The label of the row/column to be formatted.
# - pattern: The format regex pattern to apply to the values, You can use group syntax.
# - replace_with: The string or backreference to replace the matched pattern with.
# - axis:
#     - 0 or "index": Indicates a row operation.
#     - 1 or "columns": Indicates a column operation.

class FORMAT_PARAMS(BaseModel):
    table_name: str
    label: Union[str, int]
    pattern: str
    replace_with: str
    axis: Union[str, int]

def format(params: FORMAT_PARAMS):
    return

# rearrange(table_name, by_values=None, by_array=None, axis): Rearranges the rows or columns of the table based on the specified order.
# Parameters:
# - table_name: table to be rearranged.
# - by_values: If this parameter is set, the rows/columns will be rearranged based on the values in the specified row/column.
# - by_array: If this parameter is set, the rows/columns will be rearranged based on the order of the values in the array.
# - axis:
#     - 0 or "index": Indicates a row operation.
#     - 1 or "columns": Indicates a column operation.

class REARRANGE_PARAMS(BaseModel):
    table_name: str
    by_values: Optional[str]
    by_array: Optional[List[str]]
    axis: Union[str, int]

def rearrange(params: REARRANGE_PARAMS):
    pass

# divide(table_name, by=None, axis): Divides the table by the specific values of a row or column, return a list of tables.
# Parameters:
# - table (str): table to be divided.
# - by(int/str): The label of a row or column.
# - axis (str or int):
#     - 0 or "index": Indicates to divide the table by a row.
#     - 1 or "columns": Indicates to divide the table by a column.

class DIVIDE_PARAMS(BaseModel):
    table_name: str
    by: Union[str, int]
    axis: Union[str, int]

def divide(params: DIVIDE_PARAMS):
    pass

# pivot_table(table_name, index, columns, values, aggfunc): Reshapes the table so that each unique 'columns' value becomes a separate column, with the 'index' values as row headers, and the corresponding 'values' filled in their respective cells.
# Parameters:
# - table (DataFrame): The table to pivot.
# - index (str): The column name to use as the new row headers.
# - columns (str): The column name to use as the new column headers.
# - values (str): The column name whose values will fill the new table.
# - aggfunc (str): The aggregation function to apply to the values. Common options are 'first', 'sum', 'mean', etc.

class PIVOT_TABLE_PARAMS(BaseModel):
    table_name: str
    index: str
    columns: str
    values: str
    aggfunc: str

def pivot_table(params: PIVOT_TABLE_PARAMS):
    pass

# fill(table_name, method, column=None): Fills missing values in the table using the specified method.
# Parameters:
# - table: Table to fill missing values.
# - method: The method to use for filling missing values. Choose from 'value', 'mean', 'median', 'mode', 'ffill', 'bfill', 'interpolate'.
# - column: The column to fill missing values in. If None, missing values in all columns will be filled.

class FILL(BaseModel):
    table_name: str
    method: str
    column: Optional[str]

def fill(params: FILL):
    pass

# subtable(table, row_list=None, column_list=None): Returns a subtable with only the specified rows or columns.
# Parameters:
# - table_name (str): The table to extract the rows or columns from.
# - row_list (list[str/int]): The list of row labels to extract.
# - label_list (list[str/int]): The list of row/column labels to extract.

class SUBTABLE(BaseModel):
    table_name: str
    row_list: Optional[List[Union[str, int]]]
    label_list: Optional[List[Union[str, int]]]

def subtable(params: SUBTABLE):
    pass

def get_sheet_names(all_sheets):
    sheets_names = [sheet[0] for sheet in all_sheets]
    sheets_names = [sheet.split(".csv")[0] for sheet in sheets_names]
    sheets_versions = [sheet[1] for sheet in all_sheets]
    sheets_names = [f"{sheets_names[i]}_v{sheets_versions[i]}.csv" for i in range(len(sheets_names))]
    return sheets_names


def validate_dsls_functions(function_calls: List[dict], all_sheets, error_list=[]):
    valid_functions = [
        "aggregate",
        "assign",
        "blank_table",
        "concatenate",
        "copy",
        "delete_table",
        "divide",
        "drop",
        "fill",
        "format",
        "insert",
        "merge",
        "move",
        "pivot_table",
        "rearrange",
        "split",
        "subtable",
        "swap",
        "test",
        "transpose",
    ]
    sheets_names = get_sheet_names(all_sheets)
    for call in function_calls:
        if call["function_name"] not in valid_functions:
            error = create_error_message("Invalid function name", f"The function name '{call['function_name']}' is not a valid function. Please use one of the following functions: {', '.join(valid_functions)}.", call["function_name"])
            error_list.append(error)
        else:
            if call["function_name"] == "aggregate":
                validate_aggregate(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "assign":
                validate_assign(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "blank_table":
                validate_blank_table(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "concatenate":
                validate_concatenate(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "copy":
                validate_copy(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "delete_table":
                validate_delete_table(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "divide":
                validate_divide(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "drop":
                validate_drop(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "fill":
                validate_fill(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "format":
                validate_format(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "insert":
                validate_insert(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "merge":
                validate_merge(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "move":
                validate_move(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "pivot_table":
                validate_pivot_table(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "rearrange":
                validate_rearrange(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "split":
                validate_split(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "subtable":
                validate_subtable(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "swap":
                validate_swap(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "test":
                validate_test(call["arguments"], error_list, sheets_names)
            elif call["function_name"] == "transpose":
                validate_transpose(call["arguments"], error_list, sheets_names)
    return "Success"

def validate_blank_table(arguments, error_list, sheets_names):
    if len(arguments) != 2:
        error = create_error_message("Invalid number of arguments", f"The function 'blank_table' requires 2 arguments: 'row_number', 'column_number'.", "blank_table")
        error_list.append(error)
        return "Failed"
    try:
        params = BLANK_TABLE_PARAMS(row_number=arguments[0], column_number=arguments[1])
        blank_table(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'blank_table' are not in the correct format. Please check the argument types and values.", "blank_table")
        error_list.append(error)
    return "Success"
    

def validate_delete_table(arguments, error_list, sheets_names):
    if len(arguments) != 1:
        error = create_error_message("Invalid number of arguments", f"The function 'delete_table' requires 1 argument: 'table_name'.", "delete_table")
        error_list.append(error)
        return "Failed"
    try:
        params = DELETE_TABLE_PARAMS(table_name=arguments[0])
        delete_table(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The argument for 'delete_table' is not in the correct format. Please check the argument type and value.", "delete_table")
        error_list.append(error)

    if arguments[0] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' does not exist. Please create the table before performing operations on it.", "delete_table")
        error_list.append(error)
    return "Success"


def validate_insert(arguments, error_list, sheets_names):
    if len(arguments) != 4:
        error = create_error_message("Invalid number of arguments", f"The function 'insert' requires 4 arguments: 'table_name', 'index', 'index_name', 'axis'.", "insert")
        error_list.append(error)
        return "Failed"
    try:
        params = INSERT_PARAMS(table_name=arguments[0], index=arguments[1], index_name=arguments[2], axis=arguments[3])
        insert(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'insert' are not in the correct format. Please check the argument types and values.", "insert")
        error_list.append(error)

    if arguments[0] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' does not exist. Please create the table before performing operations on it.", "insert")
        error_list.append(error)
    return "Success"


def validate_drop(arguments, error_list, sheets_names):
    if len(arguments) != 3:
        error = create_error_message("Invalid number of arguments", f"The function 'drop' requires 3 arguments: 'table_name', 'label', 'axis'.", "drop")
        error_list.append(error)
        return "Failed"
    try:
        params = DROP_PARAMS(table_name=arguments[0], label=arguments[1], axis=arguments[2])
        drop(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'drop' are not in the correct format. Please check the argument types and values.", "drop")
        error_list.append(error)

    if arguments[0] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' does not exist. Please create the table before performing operations on it.", "drop")
        error_list.append(error)

    return "Success"


def validate_assign(arguments, error_list, sheets_names):
    if len(arguments) != 6:
        error = create_error_message("Invalid number of arguments", f"The function 'assign' requires 6 arguments: 'table_name', 'start_row_index', 'end_row_index', 'start_column_index', 'end_column_index', 'values'.", "assign")
        error_list.append(error)
        return "Failed"
    try:
        params = ASSIGN_PARAMS(table_name=arguments[0], start_row_index=arguments[1], end_row_index=arguments[2], start_column_index=arguments[3], end_column_index=arguments[4], values=arguments[5])
        assign(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'assign' are not in the correct format. Please check the argument types and values.", "assign")
        error_list.append(error)

    if arguments[0] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' does not exist. Please create the table before performing operations on it.", "assign")
        error_list.append(error)
    return "Success"


def validate_move(arguments, error_list, sheets_names):
    if len(arguments) != 5:
        error = create_error_message("Invalid number of arguments", f"The function 'move' requires 5 arguments: 'origin_table_name', 'origin_index', 'target_table_name', 'target_index', 'axis'.", "move")
        error_list.append(error)
        return "Failed"
    try:
        params = MOVE_PARAMS(origin_table_name=arguments[0], origin_index=arguments[1], target_table_name=arguments[2], target_index=arguments[3], axis=arguments[4])
        move(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'move' are not in the correct format. Please check the argument types and values.", "move")
        error_list.append(error)

    if arguments[0] not in sheets_names or arguments[2] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' or '{arguments[2]}' does not exist. Please create the table before performing operations on it.", "move")
        error_list.append(error)
    return "Success"


def validate_copy(arguments, error_list, sheets_names):
    if len(arguments) != 6:
        error = create_error_message("Invalid number of arguments", f"The function 'copy' requires 5 or 6 arguments: 'origin_table_name', 'origin_index', 'target_table_name', 'target_index', 'target_label_name', 'axis'.", "copy")
        error_list.append(error)
        return "Failed"
    try:
        params = COPY_PARAMS(origin_table_name=arguments[0], origin_index=arguments[1], target_table_name=arguments[2], target_index=arguments[3], target_label_name=arguments[4], axis=arguments[5])
        copy(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'copy' are not in the correct format. Please check the argument types and values.", "copy")
        error_list.append(error)

    if arguments[0] not in sheets_names or arguments[2] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' or '{arguments[2]}' does not exist. Please create the table before performing operations on it.", "copy")
        error_list.append(error)
    return "Success"


def validate_swap(arguments, error_list, sheets_names):
    if len(arguments) != 5:
        error = create_error_message("Invalid number of arguments", f"The function 'swap' requires 5 arguments: 'table_name_a', 'label_a', 'table_name_b', 'label_b', 'axis'.", "swap")
        error_list.append(error)
        return "Failed"
    try:
        params = SWAP_PARAMS(table_name_a=arguments[0], label_a=arguments[1], table_name_b=arguments[2], label_b=arguments[3], axis=arguments[4])
        swap(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'swap' are not in the correct format. Please check the argument types and values.", "swap")
        error_list.append(error)

    if arguments[0] not in sheets_names or arguments[2] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' or '{arguments[2]}' does not exist. Please create the table before performing operations on it.", "swap")
        error_list.append(error)
    return "Success"


def validate_merge(arguments, error_list, sheets_names):
    if len(arguments) != 5:
        error = create_error_message("Invalid number of arguments", f"The function 'merge' requires 6 arguments: 'table_name_a', 'table_name_b', 'how', 'on', 'left_on', 'right_on', 'axis'.", "merge")
        error_list.append(error)
        return "Failed"
    try:
        params = MERGE_PARAMS(table_name_a=arguments[0], table_name_b=arguments[1], how=arguments[2], on=arguments[3], axis=arguments[4])
        merge(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'merge' are not in the correct format. Please check the argument types and values.", "merge")
        error_list.append(error)

    if arguments[0] not in sheets_names or arguments[1] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' or '{arguments[1]}' does not exist. Please create the table before performing operations on it.", "merge")
        error_list.append(error)
    return "Success"


def validate_concatenate(arguments, error_list, sheets_names):
    if len(arguments) != 6:
        error = create_error_message("Invalid number of arguments", f"The function 'concatenate' requires 6 arguments: 'table_name', 'label_a', 'label_b', 'glue', 'new_label', 'axis'.", "concatenate")
        error_list.append(error)
        return "Failed"
    try:
        params = CONCATENATE_PARAMS(table_name=arguments[0], label_a=arguments[1], label_b=arguments[2], glue=arguments[3], new_label=arguments[4], axis=arguments[5])
        concatenate(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'concatenate' are not in the correct format. Please check the argument types and values.", "concatenate")
        error_list.append(error)

    if arguments[0] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' does not exist. Please create the table before performing operations on it.", "concatenate")
        error_list.append(error)
    return "Success"


def validate_split(arguments, error_list, sheets_names):
    if len(arguments) not in [4, 5]:
        error = create_error_message("Invalid number of arguments", f"The function 'split' requires 4 or 5 arguments: 'table_name', 'label', 'delimiter', 'axis', 'split_column'.", "split")
        error_list.append(error)
        return "Failed"
    try:
        if len(arguments) == 4:
            params = SPLIT_PARAMS(table_name=arguments[0], label=arguments[1], delimiter=arguments[2], axis=arguments[3], split_column=None)
            split(params)
        else:
            params = SPLIT_PARAMS(table_name=arguments[0], label=arguments[1], delimiter=arguments[2], axis=arguments[3], split_column=arguments[4])
            split(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'split' are not in the correct format. Please check the argument types and values.", "split")
        error_list.append(error)

    if arguments[0] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' does not exist. Please create the table before performing operations on it.", "split")
        error_list.append(error)
    return "Success"


def validate_transpose(arguments, error_list, sheets_names):
    if len(arguments) != 1:
        error = create_error_message("Invalid number of arguments", f"The function 'transpose' requires 1 argument: 'table_name'.", "transpose")
        error_list.append(error)
        return "Failed"
    try:
        transpose(arguments[0])
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The argument for 'transpose' is not in the correct format. Please check the argument type and value.", "transpose")
        error_list.append(error)

    if arguments[0] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' does not exist. Please create the table before performing operations on it.", "transpose")
        error_list.append(error)
    return "Success"


def validate_aggregate(arguments, error_list, sheets_names):
    if len(arguments) != 3:
        error = create_error_message("Invalid number of arguments", f"The function 'aggregate' requires 3 arguments: 'table_name', 'functions', 'axis'.", "aggregate")
        error_list.append(error)
        return "Failed"
    try:
        params = AGGREGATE_PARAMS(table_name=arguments[0], functions=arguments[1], axis=arguments[2])
        aggregate(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'aggregate' are not in the correct format. Please check the argument types and values.", "aggregate")
        error_list.append(error)

    if arguments[0] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' does not exist. Please create the table before performing operations on it.", "aggregate")
        error_list.append(error)
    return "Success"


def validate_test(arguments, error_list, sheets_names):
    if len(arguments) != 6:
        error = create_error_message("Invalid number of arguments", f"The function 'test' requires 6 arguments: 'table_name', 'label_a', 'label_b', 'strategy', 'axis'.", "test")
        error_list.append(error)
        return "Failed"
    try:
        params = TEST_PARAMS(table_name_a=arguments[0], label_a=arguments[1], table_name_b=arguments[2], label_b=arguments[3], strategy=arguments[4], axis=arguments[5])
        test(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'test' are not in the correct format. Please check the argument types and values.", "test")
        error_list.append(error)

    if arguments[0] not in sheets_names or arguments[2] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' or '{arguments[2]}' does not exist. Please create the table before performing operations on it.", "test")
        error_list.append(error)

def validate_format(arguments, error_list, sheets_names):
    if len(arguments) != 5:
        error = create_error_message("Invalid number of arguments", f"The function 'format' requires 4 arguments: 'table_name', 'label', 'pattern', 'axis'.", "format")
        error_list.append(error)
        return "Failed"
    try:
        params = FORMAT_PARAMS(table_name=arguments[0], label=arguments[1], pattern=arguments[2], replace_with=arguments[3], axis=arguments[4])
        format(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'format' are not in the correct format. Please check the argument types and values.", "format")
        error_list.append(error)

    if arguments[0] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' does not exist. Please create the table before performing operations on it.", "format")
        error_list.append(error)
    return "Success"

def validate_rearrange(arguments, error_list, sheets_names):
    if len(arguments) != 4:
        error = create_error_message("Invalid number of arguments", f"The function 'rearrange' requires 3 arguments: 'table_name', 'by_values', 'axis'.", "rearrange")
        error_list.append(error)
        return "Failed"
    try:
        params = REARRANGE_PARAMS(table_name=arguments[0], by_values=arguments[1], by_array=arguments[2], axis=arguments[3])
        rearrange(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'rearrange' are not in the correct format. Please check the argument types and values.", "rearrange")
        error_list.append(error)

    if arguments[0] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' does not exist. Please create the table before performing operations on it.", "rearrange")
        error_list.append(error)
    return "Success"

def validate_divide(arguments, error_list, sheets_names):
    if len(arguments) != 3:
        error = create_error_message("Invalid number of arguments", f"The function 'divide' requires 3 arguments: 'table_name', 'by', 'axis'.", "divide")
        error_list.append(error)
        return "Failed"
    try:
        params = DIVIDE_PARAMS(table_name=arguments[0], by=arguments[1], axis=arguments[2])
        divide(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'divide' are not in the correct format. Please check the argument types and values.", "divide")
        error_list.append(error)

    if arguments[0] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' does not exist. Please create the table before performing operations on it.", "divide")
        error_list.append(error)
    return "Success"

def validate_pivot_table(arguments, error_list, sheets_names):
    if len(arguments) != 5:
        error = create_error_message("Invalid number of arguments", f"The function 'pivot_table' requires 4 arguments: 'table_name', 'index', 'columns', 'values'.", "pivot_table")
        error_list.append(error)
        return "Failed"
    try:
        params = PIVOT_TABLE_PARAMS(table_name=arguments[0], index=arguments[1], columns=arguments[2], values=arguments[3], aggfunc=arguments[4])
        pivot_table(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'pivot_table' are not in the correct format. Please check the argument types and values.", "pivot_table")
        error_list.append(error)

    if arguments[0] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' does not exist. Please create the table before performing operations on it.", "pivot_table")
        error_list.append(error)
    return "Success"

def validate_fill(arguments, error_list, sheets_names):
    if len(arguments) not in [2, 3]:
        error = create_error_message("Invalid number of arguments", f"The function 'fill' requires 3 arguments: 'table_name', 'method', 'column'.", "fill")
        error_list.append(error)
        return "Failed"
    try:
        if len(arguments) == 2:
            params = FILL(table_name=arguments[0], method=arguments[1], column=None)
        elif len(arguments) == 3:
            params = FILL(table_name=arguments[0], method=arguments[1], column=arguments[2])
        fill(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'fill' are not in the correct format. Please check the argument types and values.", "fill")
        error_list.append(error)

    if arguments[0] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' does not exist. Please create the table before performing operations on it.", "fill")
        error_list.append(error)
    return "Success"

def validate_subtable(arguments, error_list, sheets_names):
    if len(arguments) != 3:
        error = create_error_message("Invalid number of arguments", f"The function 'subtable' requires 3 arguments: 'table_name', 'row_list', 'label_list'.", "subtable")
        error_list.append(error)
        return "Failed"
    try:
        params = SUBTABLE(table_name=arguments[0], row_list=arguments[1], label_list=arguments[2])
        subtable(params)
    except ValidationError as e:
        error = create_error_message("Invalid argument format", f"The arguments for 'subtable' are not in the correct format. Please check the argument types and values.", "subtable")
        error_list.append(error)

    if arguments[0] not in sheets_names:
        error = create_error_message("Table does not exist", f"The table '{arguments[0]}' does not exist. Please create the table before performing operations on it.", "subtable")
        error_list.append(error)
    return "Success"