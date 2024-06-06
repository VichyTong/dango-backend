import json

from utils.llm import create_client, get_history, append_message, generate_chat_completion, create_client


def init_prompt():
    global system_prompt, user_prompt
    with open("prompt/compile/system.txt", "r") as f:
        system_prompt = f.read()
    with open("prompt/compile/user.txt", "r") as f:
        user_prompt = f.read()


init_prompt()


def create_user_prompt(history):
    print(">>> create user prompt in compile.py")
    print(json.dumps(history, indent=4))
    start_index = 0
    for index, message in enumerate(history):
        if message["role"] == "system":
            start_index = index
            break

    information = history[start_index + 1]["content"]
    prompt = f"Information: {information}\n\n"

    question_index = 1
    for index in range(start_index + 2, len(history), 2):
        response = json.loads(history[index]["content"])
        if response["type"] == "finish":
            break

        choices = ""
        for i, choice in enumerate(response["choices"]):
            choices += f"{chr(ord('A') + i)}. {choice}\n"

        question_answer_pair = (
            user_prompt.replace("{INDEX}", str(question_index))
            .replace("{QUESTION}", response["question"])
            .replace("{CHOICES}", choices)
            .replace("{ANSWER}", history[index + 1]["content"])
        )
        question_index += 1
        prompt += question_answer_pair
    
    print(">>> user prompt created in compile.py")
    print(prompt)
    return prompt


def transfer_to_NL(dsl):
    if dsl["function_name"] == "drop":
        table = dsl["arguments"][0]
        label = dsl["arguments"][1]
        axis = dsl["arguments"][2]
        if axis == 0 or axis == "index":
            return f"Drop the row $[{label}] in %[{table}]."
        elif axis == 1 or axis == "column":
            return f"Drop the column $[{label}] in %[{table}]."
        else:
            return "Invalid function"
    elif dsl["function_name"] == "move":
        table = dsl["arguments"][0]
        label = dsl["arguments"][1]
        target_table = dsl["arguments"][2]
        target_position = dsl["arguments"][3]
        axis = dsl["arguments"][4]
        if axis == 0 or axis == "index":
            return f"Move the row $[{label}] in %[{table}] to %[{target_table}] at position #[{target_position}]."
        elif axis == 1 or axis == "column":
            return f"Move the column $[{label}] in %[{table}] to %[{target_table}] at position #[{target_position}]."
        else:
            return "Invalid function"
    elif dsl["function_name"] == "copy":
        table = dsl["arguments"][0]
        label = dsl["arguments"][1]
        target_table = dsl["arguments"][2]
        target_position = dsl["arguments"][3]
        axis = dsl["arguments"][4]
        if axis == 0 or axis == "index":
            return f"Copy the row $[{label}] in %[{table}] to %[{target_table}] at position #[{target_position}]."
        elif axis == 1 or axis == "column":
            return f"Copy the column $[{label}] in %[{table}] to %[{target_table}] at position #[{target_position}]."
        else:
            return "Invalid function"
    elif dsl["function_name"] == "merge":
        table = dsl["arguments"][0]
        label_1 = dsl["arguments"][1]
        label_2 = dsl["arguments"][2]
        glue = dsl["arguments"][3]
        new_label = dsl["arguments"][4]
        axis = dsl["arguments"][5]
        if axis == 0 or axis == "index":
            return f"Merge the row $[{label_1}] and $[{label_2}] in %[{table}] with @{glue} as $[{new_label}]."
        elif axis == 1 or axis == "column":
            return f"Merge the column $[{label_1}] and $[{label_2}] in %[{table}] with @{glue} as $[{new_label}]."
        else:
            return "Invalid function"
    elif dsl["function_name"] == "split":
        table = dsl["arguments"][0]
        label = dsl["arguments"][1]
        delimiter = dsl["arguments"][2]
        new_labels = dsl["arguments"][3]
        axis = dsl["arguments"][4]
        if axis == 0 or axis == "index":
            return f"Split the row $[{label}] in %[{table}] by &[{delimiter}] as $[{new_labels}]."
        elif axis == 1 or axis == "column":
            return f"Split the column $[{label}] in %[{table}] by &[{delimiter}] as $[{new_labels}]."
        else:
            return "Invalid function"
    elif dsl["function_name"] == "transpose":
        table = dsl["arguments"][0]
        return f"Transpose %[{table}]."
    elif dsl["function_name"] == "aggregate":
        table = dsl["arguments"][0]
        label = dsl["arguments"][1]
        operation = dsl["arguments"][2]
        axis = dsl["arguments"][3]
        if axis == 0 or axis == "index":
            return f"Aggregate the row $[{label}] in %[{table}] with *[{operation}]."
        elif axis == 1 or axis == "column":
            return f"Aggregate the column $[{label}] in %[{table}] with *[{operation}]."
        else:
            return "Invalid function"


def dsl_compile(client_id: str) -> str:
    history = get_history(client_id)
    user_prompt = create_user_prompt(history)

    tmp_client_id = create_client()
    append_message(tmp_client_id, system_prompt, "system")
    append_message(tmp_client_id, user_prompt, "user")
    response = generate_chat_completion(tmp_client_id)
    print(">>> dsl_compile -- raw DSL:")
    print(response)
    dsls = json.loads(response)
    for dsl in dsls:
        dsl["natural_language"] = transfer_to_NL(dsl)
    print(dsls)
    return dsls
