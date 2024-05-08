from typing import List
from utils.llm import create_client, get_client
import json


def init_prompt():
    global transfer_prompt
    global analyze_system_prompt, analyze_user_prompt, analyze_few_shot_user_prompt, analyze_few_shot_assistant_prompt
    with open("prompt/analyze/transfer_meta_diff_to_NL.txt", "r") as f:
        transfer_prompt = f.read()
    with open("prompt/analyze/system.txt", "r") as f:
        analyze_system_prompt = f.read()
    with open("prompt/analyze/user.txt", "r") as f:
        analyze_user_prompt = f.read()


init_prompt()


def extract_changes(data):
    # Split the input string into lines
    lines = data.strip().split("\n")

    # Prepare a list to hold all changes
    changes = []

    # Process each line
    for line in lines:
        # Remove 'Row:', 'Col:', 'Old:', and 'New:' and split by commas
        parts = (
            line.replace("Row: ", "")
            .replace("Col: ", "")
            .replace("Old: ", "")
            .replace("New: ", "")
            .split(", ")
        )

        # Create a dictionary for each line and append to the list
        change = {
            "row": int(parts[0]),
            "col": int(parts[1]),
            "old_value": parts[2],
            "new_value": parts[3],
        }
        changes.append(change)

    return changes


def find_batch_operation(changes, num_rows, num_cols):
    changed_row_flag = 0
    changed_col_flag = 0
    for index, change in enumerate(changes):
        if change["row"] == changed_row_flag + 1:
            changed_row_flag = change["row"]
        else:
            changed_row_flag = 0
        if change["col"] == changed_col_flag + 1:
            changed_col_flag = change["col"]
        else:
            changed_col_flag = 0
        if changed_row_flag == num_rows:
            new_change = {
                "col": change["col"],
                "old_value": change ["old_value"],
                "new_value": change["new_value"],
            }
        # TODO here ...
        


def mata_diff_to_NL(diff: str, row_count: int, column_names: list) -> str:
    changes = extract_changes(diff)
    for change in changes:
        change["row"] += 1
        change["col"] += 1
    # changes = find_batch_operation(changes, row_count, len(column_names))
    print(changes)
    client_id, client = create_client()
    client.append_system_message(transfer_prompt)
    client.append_user_message(diff)
    response = client.generate_chat_completion()
    client.append_assistant_message(response)
    print(json.dumps(client.history, indent=4))
    return response


def get_analyze(sheet_id, row_count, column_names, NL_diff, user_prompt):
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
        analyze_user_prompt.replace("{sheet_id}", sheet_id)
        .replace("{row_count}", str(row_count))
        .replace("{column_names}", column_names)
        .replace("{NL_diff}", NL_diff)
        .replace("{user_prompt}", user_prompt)
        .replace("{column_number}", str(column_number))
    )

    client_id, client = create_client()
    client.append_system_message(analyze_system_prompt)
    client.append_user_message(input_user_prompt)
    response = client.generate_chat_completion()
    print(response)
    client.append_assistant_message(response)
    print(json.dumps(client.history, indent=4))
    return client_id, response


def analyze(
    sheet_id: str,
    row_count: int,
    column_names: List[str],
    table_diff: str,
    user_promt: str,
) -> str:
    NL_diff = mata_diff_to_NL(table_diff, row_count, column_names)
    client_id, response = get_analyze(
        sheet_id, row_count, column_names, NL_diff, user_promt
    )
    response = json.loads(response)

    return client_id, response
