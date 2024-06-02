import json

from utils.llm import get_history, append_message, generate_chat_completion


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

    history = get_history(client_id)
    append_message(client_id, system_prompt, "system")
    append_message(client_id, input_user_prompt, "user")

    response = generate_chat_completion(client_id)
    print(response)
    append_message(client_id, response, "assistant")
    response = json.loads(response)
    return response
