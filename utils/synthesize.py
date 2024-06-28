import json

from utils.llm import (
    append_message,
    generate_chat_completion,
)
from utils.db import get_history_text, get_history


def init_prompt():
    global summarize_system_prompt
    global plan_system_prompt, plan_user_prompt_template
    global generate_system_prompt, generate_user_prompt_template
    with open("prompt/synthesize/summarize_system.txt", "r") as f:
        summarize_system_prompt = f.read()
    with open("prompt/synthesize/plan_system.txt", "r") as f:
        plan_system_prompt = f.read()
    with open("prompt/synthesize/plan_user.txt", "r") as f:
        plan_user_prompt_template = f.read()
    with open("prompt/synthesize/generate_system.txt", "r") as f:
        generate_system_prompt = f.read()
    with open("prompt/synthesize/generate_user.txt", "r") as f:
        generate_user_prompt_template = f.read()


init_prompt()


def create_generate_user_prompt(summarization):
    return generate_user_prompt_template.replace("{PLAN}", summarization)


def transfer_to_NL(dsl):
    if dsl["function_name"] == "drop":
        table = dsl["arguments"][0]
        label = dsl["arguments"][1]
        axis = dsl["arguments"][2]
        if axis == 0 or axis == "index" or axis == "0":
            return f"Drop the row $[{label}] in %[{table}]."
        elif axis == 1 or axis == "columns" or axis == "1":
            return f"Drop the column $[{label}] in %[{table}]."
        else:
            return "Invalid function"
    elif dsl["function_name"] == "move":
        table = dsl["arguments"][0]
        label = dsl["arguments"][1]
        target_table = dsl["arguments"][2]
        target_position = dsl["arguments"][3]
        axis = dsl["arguments"][4]
        if axis == 0 or axis == "index" or axis == "0":
            return f"Move the row $[{label}] in %[{table}] to %[{target_table}] at position #[{target_position}]."
        elif axis == 1 or axis == "columns" or axis == "1":
            return f"Move the column $[{label}] in %[{table}] to %[{target_table}] at position #[{target_position}]."
        else:
            return "Invalid function"
    elif dsl["function_name"] == "copy":
        table = dsl["arguments"][0]
        label = dsl["arguments"][1]
        target_table = dsl["arguments"][2]
        target_position = dsl["arguments"][3]
        axis = dsl["arguments"][4]
        if axis == 0 or axis == "index" or axis == "0":
            return f"Copy the row $[{label}] in %[{table}] to %[{target_table}] at position #[{target_position}]."
        elif axis == 1 or axis == "columns" or axis == "1":
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
        if axis == 0 or axis == "index" or axis == "0":
            return f"Merge the row $[{label_1}] and $[{label_2}] in %[{table}] with @{glue} as $[{new_label}]."
        elif axis == 1 or axis == "columns" or axis == "1":
            return f"Merge the column $[{label_1}] and $[{label_2}] in %[{table}] with @{glue} as $[{new_label}]."
        else:
            return "Invalid function"
    elif dsl["function_name"] == "split":
        table = dsl["arguments"][0]
        label = dsl["arguments"][1]
        delimiter = dsl["arguments"][2]
        new_labels = dsl["arguments"][3]
        axis = dsl["arguments"][4]
        if axis == 0 or axis == "index" or axis == "0":
            return f"Split the row $[{label}] in %[{table}] by &[{delimiter}] as $[{new_labels}]."
        elif axis == 1 or axis == "columns" or axis == "1":
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
        if axis == 0 or axis == "index" or axis == "0":
            return f"Aggregate the row $[{label}] in %[{table}] with *[{operation}]."
        elif axis == 1 or axis == "columns" or axis == "1":
            return f"Aggregate the column $[{label}] in %[{table}] with *[{operation}]."
        else:
            return "Invalid function"


def dsl_synthesize(client_id: str) -> str:
    history = get_history(client_id)
    summarize_user_prompt = get_history_text(client_id)

    messages = append_message(summarize_system_prompt, "system")
    messages = append_message(summarize_user_prompt, "user", messages)
    summarization = generate_chat_completion(messages)

    print(f"\033[0;34;40m>>> Summarization assistant")
    print(summarize_user_prompt)
    print("--------------------------")
    print("'''")
    print(summarization)
    print("'''")

    plan_user_prompt = plan_user_prompt_template.replace(
        "{USER_INTENTS}", summarization
    ).replace("{INFORMATION}", history["information"])

    messages = append_message(plan_system_prompt, "system")
    messages = append_message(plan_user_prompt, "user", messages)
    response = generate_chat_completion(messages)

    print(f"\033[0;35;40m>>> Planning assistant")
    print(plan_user_prompt)
    print("--------------------------")
    print("'''")
    print(response)
    print("'''")

    generate_user_prompt = create_generate_user_prompt(response)
    messages = append_message(generate_system_prompt, "system")
    messages = append_message(generate_user_prompt, "user", messages)
    response = generate_chat_completion(messages)

    print(f"\033[0;36;40m>>> DSL generation assistant")
    print(generate_user_prompt)
    print("--------------------------")
    print("'''")
    print(response)
    print("'''")
    dsls = json.loads(response)
    for dsl in dsls:
        dsl["natural_language"] = transfer_to_NL(dsl)
    return dsls
