import json

from utils.llm import get_client


def init_prompt():
    global system_prompt
    global user_prompt
    with open("prompt/simple_chat/system.txt", "r") as f:
        system_prompt = f.read()
    with open("prompt/simple_chat/user.txt", "r") as f:
        user_prompt = f.read()


init_prompt()


def simple_analyze(client_id, sheet_id, version, row_names, column_names, prompt):
    index = "A"
    column_string_list = []
    for item in column_names:
        item = f'{index}: "{item}"'
        index = chr(ord(index) + 1)
        column_string_list.append(item)
        # TODO: What if number of columns is more than 26?
    column_names = ", ".join(column_string_list)
    
    sheet_name = f"{sheet_id.split('.')[0]}_v{version}.{sheet_id.split('.')[1]}"
    input_user_prompt = (
        user_prompt.replace(
            "{sheet_id}",
            sheet_name,
        )
        .replace("{row_count}", str(len(row_names)))
        .replace("{column_names}", column_names)
        .replace("{column_count}", str(len(column_names)))
        .replace("{user_prompt}", prompt)
    )

    client = get_client(client_id)
    client.append_system_message(system_prompt)
    client.append_user_message(input_user_prompt)

    response = client.generate_chat_completion()
    print(response)
    client.append_assistant_message(response)
    response = json.loads(response)
    return response
