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
    with open("prompt/analyze/few_shot_user_1.txt", "r") as f:
        analyze_few_shot_user_prompt = f.read()
    with open("prompt/analyze/few_shot_assistant_1.txt", "r") as f:
        analyze_few_shot_assistant_prompt = f.read()


init_prompt()


def mata_diff_to_NL(diff: str) -> str:
    client_id, client = create_client()
    client.append_system_message(transfer_prompt)
    client.append_user_message(diff)
    response = client.generate_chat_completion()
    client.append_assistant_message(response)
    print(json.dumps(client.history, indent=4))
    return response


def get_analyze(sheet_id, row_count, column_names, NL_diff, user_prompt):
    input_user_prompt = (
        analyze_user_prompt.replace("{sheet_id}", sheet_id)
        .replace("{row_count}", str(row_count))
        .replace("{column_names}", f"[{', '.join(column_names)}]")
        .replace("{NL_diff}", NL_diff)
        .replace("{user_prompt}", user_prompt)
    )

    client_id, client = create_client()
    client.append_system_message(analyze_system_prompt)
    # client.append_user_message(analyze_few_shot_user_prompt)
    # client.append_assistant_message(analyze_few_shot_assistant_prompt)
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
    NL_diff = mata_diff_to_NL(table_diff)
    client_id, response = get_analyze(
        sheet_id, row_count, column_names, NL_diff, user_promt
    )
    response = json.loads(response)

    return client_id, response
