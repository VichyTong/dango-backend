from typing import List
import json
import re

from utils.llm import (
    create_client,
    get_history,
    append_message,
    generate_chat_completion,
)


def init_prompt():
    global transfer_prompt
    global analyze_system_prompt, analyze_user_prompt
    global multi_analyze_system_prompt, multi_analyze_user_prompt, multi_analyze_diff_prompt
    with open("prompt/analyze/transfer_meta_diff_to_NL.txt", "r") as f:
        transfer_prompt = f.read()
    with open("prompt/analyze/system.txt", "r") as f:
        analyze_system_prompt = f.read()
    with open("prompt/analyze/user.txt", "r") as f:
        analyze_user_prompt = f.read()
    with open("prompt/multi_analyze/system.txt", "r") as f:
        multi_analyze_system_prompt = f.read()
    with open("prompt/multi_analyze/user.txt", "r") as f:
        multi_analyze_user_prompt = f.read()
    with open("prompt/multi_analyze/diff.txt", "r") as f:
        multi_analyze_diff_prompt = f.read()


init_prompt()


def extract_changes(data):
    lines = data.strip().split("\n")
    changes = []

    # change pattern
    pattern_1 = r'Row: (\d+|\d+\.\d+), Col: (\d+|\d+\.\d+), Old: ([a-zA-Z]*|\d+|\d+\.\d+| )\r?, New: ([a-zA-Z]*|\d+|\d+\.\d+| )\r?'
    # create row pattern
    pattern_2 = r"Created row at index (\d+)"
    # create column pattern
    pattern_3 = r"Created column at index (\d+)"
    # copy cloumn pattern 
    pattern_4 = r'Copied data from (\d+):(\d+) to (\d+):(\d+) \(col, row\)'
    

    for line in lines:
        match_1 = re.match(pattern_1, line)
        if match_1:
            change = {
                "type": "change",
                "row": int(match_1.group(1)),
                "col": int(match_1.group(2)),
                "old_value": match_1.group(3),
                "new_value": match_1.group(4),
            }
            print("---------------")
            print(change)
            print("---------------")
            changes.append(change)
            continue

        match_2 = re.match(pattern_2, line)
        if match_2:
            change = {
                "type": "create_row",
                "row": int(match_2.group(1)),
            }
            changes.append(change)
            continue
        
        match_3 = re.match(pattern_3, line)
        if match_3:
            change = {
                "type": "create_col",
                "col": int(match_3.group(1)),
            }
            changes.append(change)
            continue

        match_4 = re.match(pattern_4, line)
        if match_4:
            change = {
                "type": "copy_col",
                "start_col": int(match_4.group(1)),
                "start_row": int(match_4.group(2)),
                "end_col": int(match_4.group(3)),
                "end_row": int(match_4.group(4)),
            }
            changes.append(change)
            continue

        print(f"WARN: Unrecognized line: {line}")

    return changes


def find_batch_operation(changes, num_rows, num_cols):
    # List to store detected batch operations
    batch_operations = []
    # 1. batch create row operations
    next_index = num_rows + 1

    for change in changes:
        if change["type"] == "create_row":
            if change["row"] == next_index:
                next_index += 1

    if next_index != num_rows + 1:
        batch_operations.append({
            "type": "create_multi_rows",
            "start_row": num_rows + 1,
            "end_row": next_index - 1,
        })

    changes = [change for change in changes if change["type"] != "create_row"]
    num_rows = next_index - 1

    # 2. batch create column operations
    next_index = num_cols + 1

    for change in changes:
        if change["type"] == "create_col":
            if change["col"] == next_index:
                next_index += 1

    if next_index != num_cols + 1:
        batch_operations.append({
            "type": "create_multi_cols",
            "start_col": num_cols + 1,
            "end_col": next_index - 1,
        })

    changes = [change for change in changes if change["type"] != "create_col"]
    num_cols = next_index - 1

    # 3. batch change operations
    # Initialize dictionaries to track changes across rows and columns
    col_changes = {col: [] for col in range(0, num_cols + 1)}
    row_changes = {row: [] for row in range(0, num_rows + 1)}

    # Gather changes by rows and columns
    for change in changes:
        if change["type"] != "change":
            continue
        col_changes[change["col"]].append(change)
        row_changes[change["row"]].append(change)

    # Check for column-wise batch operations
    for col, col_changes in col_changes.items():
        if (
            len(col_changes) == num_rows
            and all(
                change["row"] == i
                for i, change in enumerate(
                    sorted(col_changes, key=lambda x: x["row"]), start=1
                )
            )
        ) or (
            len(col_changes) == num_rows + 1
            and all(
                change["row"] == i
                for i, change in enumerate(
                    sorted(col_changes, key=lambda x: x["row"]), start=0
                )
            )
        ):
            # All rows in this column have changes
            old_values = [
                change["old_value"]
                for change in sorted(col_changes, key=lambda x: x["row"])
            ]
            new_values = [
                change["new_value"]
                for change in sorted(col_changes, key=lambda x: x["row"])
            ]
            batch_operations.append(
                {
                    "type": "all_row",
                    "col": col,
                    "old_values": old_values,
                    "new_values": new_values,
                }
            )
            # Remove individual changes from the main list
            for change in col_changes:
                changes.remove(change)

    # Check for row-wise batch operations
    for row, row_changes in row_changes.items():
        if (
            len(row_changes) == num_cols
            and all(
                change["col"] == i
                for i, change in enumerate(
                    sorted(row_changes, key=lambda x: x["col"]), start=1
                )
            )
        ) or (
            len(row_changes) == num_cols + 1
            and all(
                change["col"] == i
                for i, change in enumerate(
                    sorted(row_changes, key=lambda x: x["col"]), start=0
                )
            )
        ):
            # All columns in this row have changes
            old_values = [
                change["old_value"]
                for change in sorted(row_changes, key=lambda x: x["col"])
            ]
            new_values = [
                change["new_value"]
                for change in sorted(row_changes, key=lambda x: x["col"])
            ]
            batch_operations.append(
                {
                    "type": "all_col",
                    "row": row,
                    "old_values": old_values,
                    "new_values": new_values,
                }
            )
            # Remove individual changes from the main list
            for change in row_changes:
                changes.remove(change)

    # Add batch operations to the changes list
    changes.extend(batch_operations)

    return changes


def mata_diff_to_NL(
    diff: str, row_count: int, column_names: list, is_index_table: bool
) -> str:
    changes = extract_changes(diff)
    if is_index_table:
        for change in changes:
            if "col" in change:
                change["col"] += 1
    changes = find_batch_operation(changes, row_count, len(column_names))
    print(">>> Finding batch operations...")
    print(changes)

    changes_text = ""
    for change in changes:
        changes_text += json.dumps(change) + "\n"

    client_id = create_client()
    append_message(client_id, transfer_prompt, "system")
    append_message(client_id, changes_text, "user")
    response = generate_chat_completion(client_id)
    append_message(client_id, response, "assistant")
    history = get_history(client_id)
    print(json.dumps(history, indent=4))
    return response


def get_analyze(
    client_id, sheet_id, version, row_count, column_names, NL_diff, user_prompt
):
    column_number = len(column_names)
    index = "A"
    column_string_list = []
    for item in column_names:
        item = f'{index}: "{item}"'
        index = chr(ord(index) + 1)
        column_string_list.append(item)
        # TODO: What if number of columns is more than 26?
    column_names = ", ".join(column_string_list)

    input_user_prompt = (
        analyze_user_prompt.replace(
            "{sheet_id}",
            f"{sheet_id.split('.')[0]}_v{version}.{sheet_id.split('.')[1]}",
        )
        .replace("{row_count}", str(row_count))
        .replace("{column_names}", column_names)
        .replace("{column_count}", str(column_number))
        .replace("{NL_diff}", NL_diff)
        .replace("{user_prompt}", user_prompt)
    )

    history = get_history(client_id)
    append_message(client_id, analyze_system_prompt, "system")
    append_message(client_id, input_user_prompt, "user")
    response = generate_chat_completion(client_id)
    print(response)
    append_message(client_id, response, "assistant")
    print(json.dumps(history, indent=4))
    return response


def analyze(
    client_id: str,
    sheet_id: str,
    version: int,
    row_count: int,
    column_names: List[str],
    table_diff: str,
    user_promt: str,
    is_index_table: bool,
) -> str:
    NL_diff = mata_diff_to_NL(table_diff, row_count, column_names, is_index_table)
    response = get_analyze(
        client_id, sheet_id, version, row_count, column_names, NL_diff, user_promt
    )
    response = json.loads(response)

    return response


def get_multi_analyze(client_id, table_list, user_prompt):
    input_user_prompt = ""
    for index, table in enumerate(table_list, start=1):
        column_names = table["column_names"]
        column_number = len(column_names)
        sheet_id = table["sheet_id"]
        version = table["version"]
        file_name = f"{sheet_id.split('.')[0]}_v{version}.{sheet_id.split('.')[1]}"
        row_count = len(table["row_names"])

        column_index = "A"
        column_string_list = []
        for item in column_names:
            item = f'{column_index}: "{item}"'
            column_index = chr(ord(column_index) + 1)
            column_string_list.append(item)
            # TODO: What if number of columns is more than 26?
        column_names = ", ".join(column_string_list)

        input_user_prompt += (
            multi_analyze_user_prompt.replace("{index}", str(index))
            .replace("{file_name}", file_name)
            .replace("{column_count}", str(column_number))
            .replace("{column_names}", column_names)
            .replace("{row_count}", str(row_count))
        )
        if "NL_diff" in table:
            input_user_prompt += multi_analyze_diff_prompt.replace(
                "{NL_diff}", table["NL_diff"]
            )

    if user_prompt == "":
        user_prompt = "\nUser Prompt: (No user prompt)"
    else:
        user_prompt = "\nUser Prompt: " + user_prompt

    input_user_prompt += user_prompt

    print("\n>>> final_input_user_prompt:")
    print("'''")
    print(input_user_prompt)
    print("'''\n")

    history = get_history(client_id)
    append_message(client_id, multi_analyze_system_prompt, "system")
    append_message(client_id, input_user_prompt, "user")
    response = generate_chat_completion(client_id)
    append_message(client_id, response, "assistant")
    return response


def multi_analyze(
    client_id: str,
    table_list: List[dict],
    user_promt: str,
) -> str:
    for table in table_list:
        sheet_id = table["sheet_id"]
        version = table["version"]
        row_count = len(table["row_names"])
        column_names = table["column_names"]
        table_diff = table["table_diff"]
        is_index_table = table["is_index_table"]
        if table_diff:
            NL_diff = mata_diff_to_NL(
                table_diff, row_count, column_names, is_index_table
            )
            table["NL_diff"] = NL_diff

    print(">>> multi analyze table_list")
    print(table_list)

    response = get_multi_analyze(client_id, table_list, user_promt)

    response = json.loads(response)
    return response
