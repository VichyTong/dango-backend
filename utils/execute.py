import re
import json
import pandas as pd
from utils.db import (
    upload_sheet,
    get_sheet,
    delete_sheet,
    get_same_sheet_version,
    find_next_version,
)
from utils.log import log_text

from dsl.utils import (
    insert,
    drop,
    assign,
    move,
    copy,
    swap,
    merge,
    concatenate,
    split,
    transpose,
    aggregate,
    test,
    rearrange,
    format,
    divide,
    pivot_table,
    fill,
    sub_table,
)


def execute_dsl(sheet, function, arguments, target_sheet=None, condition=None):
    if function == "insert":
        return insert(sheet, *arguments)
    elif function == "drop":
        return drop(sheet, *arguments, condition)
    elif function == "assign":
        return assign(sheet, *arguments)
    elif function == "copy":
        return copy(sheet, arguments[0], target_sheet, *arguments[1:])
    elif function == "move":
        return move(sheet, arguments[0], target_sheet, *arguments[1:])
    elif function == "swap":
        return swap(sheet, arguments[0], target_sheet, *arguments[1:])
    elif function == "merge":
        return merge(sheet, target_sheet, *arguments)
    elif function == "concatenate":
        return concatenate(sheet, *arguments)
    elif function == "split":
        return split(sheet, *arguments)
    elif function == "transpose":
        return transpose(sheet)
    elif function == "aggregate":
        return aggregate(sheet, *arguments)
    elif function == "test":
        return test(sheet, *arguments)
    elif function == "rearrange":
        return rearrange(sheet, *arguments)
    elif function == "format":
        return format(sheet, *arguments)
    elif function == "divide":
        return divide(sheet, *arguments)
    elif function == "pivot_table":
        return pivot_table(sheet, *arguments)
    elif function == "fill":
        return fill(sheet, *arguments)
    elif function == "sub_table":
        return sub_table(sheet, *arguments)
    else:
        return "Invalid function"

def execute_dsl_list(client_id, dsl_list, DependenciesManager):
    # table-level operations
    table_function_list = [
        "delete_table",
        "create_table",
        "pivot_table",
        "sub_table",
    ]
    # table_name in arguments[0]
    type_a_function_list = [
        "insert",
        "drop",
        "assign",
        "concatenate",
        "split",
        "transpose",
        "aggregate",
        "test",
        "format",
        "rearrange",
        "divide",
        "fill",
    ]
    # table_name_a in arguments[0], table_name_b in arguments[2]
    type_b_function_list = [
        "move",
        "copy",
        "swap",
    ]
    # table_name_a in arguments[0], table_name_b in arguments[1]
    type_c_function_list = [
        "merge",
    ]

    def split_sheet_name(sheet_name):
        # Regular expression to find "v{int}" suffix
        match = re.search(r"_v(\d+)\.csv$", sheet_name)
        if match:
            # Extract base name and version number
            base_name = sheet_name[: match.start()] + ".csv"
            version = int(match.group(1))
        else:
            # No version number present
            base_name = sheet_name
            version = 0

        return base_name, version

    def get_sheet_info(sheet_name):
        sheet_id, version = split_sheet_name(sheet_name)
        sheet_data = get_sheet(client_id, sheet_id, version)
        sheet = pd.DataFrame(sheet_data)
        if "Unnamed: 0" in sheet.columns:
            sheet = pd.DataFrame(sheet_data, index_col=0)
        return sheet

    tmp_sheet_data_map = {}
    tmp_sheet_version_map = {}
    delete_table_list = []

    def load_sheet(sheet_name):
        sheet_id, sheet_version = split_sheet_name(sheet_name)
        if sheet_id not in tmp_sheet_data_map:
            tmp_sheet_data_map[sheet_id] = get_sheet_info(sheet_name)
            tmp_sheet_version_map[sheet_id] = sheet_version
        else:
            if tmp_sheet_version_map[sheet_id] != sheet_version:
                log_text(
                    client_id,
                    f">>> Execute_DSL\nError: {sheet_id} version {tmp_sheet_version_map[sheet_id]} and {sheet_version} mismatch.",
                )
                return None

    for dsl in dsl_list:
        function = dsl.function_name
        arguments = dsl.arguments
        try:
            condition = dsl.condition
        except AttributeError:
            condition = None
        DependenciesManager.update_dependency(function, arguments)
        if function in table_function_list:
            if function == "create_table":
                # create a dataframe have row_number and column_number
                sheet_id = arguments[0]
                row_number = arguments[1]
                column_number = arguments[2]
                data = pd.DataFrame(
                    index=range(row_number), columns=range(column_number)
                )
                upload_sheet(client_id, sheet_id, 0, data.to_dict())
                tmp_sheet_data_map[sheet_id] = data
                tmp_sheet_version_map[sheet_id] = 0
            elif function == "delete_table":
                sheet_id, version = split_sheet_name(arguments[0])
                delete_sheet(
                    client_id,
                    sheet_id=sheet_id,
                    version=version,
                )
                delete_table_list.append(
                    {
                        "sheet_id": sheet_id,
                        "version": version,
                    }
                )
            elif function == "pivot_table":
                load_sheet(arguments[0])
                sheet_id, _ = split_sheet_name(arguments[0])
                sheet = tmp_sheet_data_map[sheet_id]
                new_sheet = execute_dsl(sheet, function, arguments[1:])
                upload_sheet(client_id, "Pivot_Result.csv", 0, new_sheet.to_dict())
                tmp_sheet_data_map["Pivot_Result.csv"] = new_sheet
                tmp_sheet_version_map["Pivot_Result.csv"] = 0
            elif function == "sub_table":
                load_sheet(arguments[0])
                sheet_id, _ = split_sheet_name(arguments[0])
                new_name = arguments[2]
                sheet = tmp_sheet_data_map[sheet_id]
                new_sheet = execute_dsl(sheet, function, arguments[1:])
                upload_sheet(client_id, new_name, 0, new_sheet.to_dict())
                tmp_sheet_data_map[new_name] = new_sheet
                tmp_sheet_version_map[new_name] = 0
        elif function in type_a_function_list:
            load_sheet(arguments[0])
            sheet_id, _ = split_sheet_name(arguments[0])
            sheet = tmp_sheet_data_map[sheet_id]
            new_sheet = execute_dsl(sheet, function, arguments[1:], condition=condition)
            if function == "test":
                tmp_sheet_data_map["Test_Result.csv"] = new_sheet
                upload_sheet(client_id, "Test_Result.csv", 0, new_sheet.to_dict())
            elif function == "divide":
                for group_sheet in new_sheet:
                    unique_value = group_sheet["unique_value"]
                    data = group_sheet["data"]
                    tmp_sheet_data_map[unique_value] = data
                    upload_sheet(client_id, unique_value, 0, data.to_dict())
            else:
                tmp_sheet_data_map[sheet_id] = new_sheet
        elif function in type_b_function_list:
            load_sheet(arguments[0])
            load_sheet(arguments[2])
            sheet_id, _ = split_sheet_name(arguments[0])
            target_sheet_id, _ = split_sheet_name(arguments[2])
            sheet = tmp_sheet_data_map[sheet_id]
            target_sheet = tmp_sheet_data_map[target_sheet_id]
            new_sheet, new_target_sheet = execute_dsl(
                sheet,
                function,
                [arguments[1]] + arguments[3:],
                target_sheet=target_sheet,
            )
            tmp_sheet_data_map[sheet_id] = new_sheet
            tmp_sheet_data_map[target_sheet_id] = new_target_sheet
        elif function in type_c_function_list:
            load_sheet(arguments[0])
            load_sheet(arguments[1])
            sheet_id, _ = split_sheet_name(arguments[0])
            target_sheet_id, _ = split_sheet_name(arguments[1])
            sheet = tmp_sheet_data_map[sheet_id]
            target_sheet = tmp_sheet_data_map[target_sheet_id]
            if function == "merge":
                merged_table = execute_dsl(
                    sheet,
                    function,
                    arguments[2:],
                    target_sheet=target_sheet,
                )
                tmp_sheet_data_map["merged.csv"] = merged_table
                upload_sheet(client_id, "merged.csv", 0, merged_table.to_dict())
                continue
            new_sheet, new_target_sheet = execute_dsl(
                sheet,
                function,
                arguments[2:],
                target_sheet=target_sheet,
            )
            tmp_sheet_data_map[sheet_id] = new_sheet
            tmp_sheet_data_map[target_sheet_id] = new_target_sheet
        else:
            return "Error: Invalid function"

    output = []
    for sheet_id, sheet in tmp_sheet_data_map.items():
        sheet_data = sheet.fillna("").to_dict()
        same_sheet_version = get_same_sheet_version(client_id, sheet_id, sheet_data)
        if same_sheet_version is not None:
            print(f"Sheet {sheet_id} already exists in version {same_sheet_version}")
            output.append(
                {
                    "sheet_id": sheet_id,
                    "version": same_sheet_version,
                    "data": sheet.fillna("").to_dict(orient="list"),
                    "is_delete": False,
                }
            )
            continue
        sheet_version = find_next_version(client_id, sheet_id)
        upload_sheet(client_id, sheet_id, sheet_version, sheet_data)
        output.append(
            {
                "sheet_id": sheet_id,
                "version": sheet_version,
                "data": sheet.fillna("").to_dict(orient="list"),
                "is_delete": False,
            }
        )
    for table in delete_table_list:
        output.append(
            {
                "sheet_id": table["sheet_id"],
                "version": table["version"],
                "data": [],
                "is_delete": True,
            }
        )
    print(json.dumps(output, indent=4))