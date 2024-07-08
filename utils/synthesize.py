import json

from utils.llm import (
    append_message,
    generate_chat_completion,
)
from utils.db import get_history
from utils.log import log_messages
from utils.format_text import get_history_text, format_information


def init_prompt():
    global summarize_system_prompt
    global plan_system_prompt, plan_user_prompt_template
    global generate_system_prompt, generate_user_prompt_template
    global verifier_system_prompt, verifier_user_prompt_template
    global plan_with_feedback_user_prompt, generate_with_feedback_user_prompt
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
    with open("prompt/synthesize/verifier_system.txt", "r") as f:
        verifier_system_prompt = f.read()
    with open("prompt/synthesize/verifier_user.txt", "r") as f:
        verifier_user_prompt_template = f.read()
    with open("prompt/synthesize/plan_with_feedback_user.txt", "r") as f:
        plan_with_feedback_user_prompt = f.read()
    with open("prompt/synthesize/generate_with_feedback_user.txt", "r") as f:
        generate_with_feedback_user_prompt = f.read()


init_prompt()


def transfer_to_NL(dsl):
    if dsl["function_name"] == "create_table":
        table = dsl["arguments"][0]
        row_number = dsl["arguments"][1]
        column_number = dsl["arguments"][2]
        return f"Create a table %[{table}] with {row_number} rows and {column_number} columns."
    elif dsl["function_name"] == "delete_table":
        table = dsl["arguments"][0]
        return f"Delete the table %[{table}]."
    elif dsl["function_name"] == "insert":
        table = dsl["arguments"][0]
        index = dsl["arguments"][1]
        index_name = dsl["arguments"][2]
        axis = dsl["arguments"][3]
        if axis == 0 or axis == "index" or axis == "0":
            return f"Insert a row $[{index_name}] at position #[{index}] in %[{table}]."
        elif axis == 1 or axis == "columns" or axis == "1":
            return (
                f"Insert a column $[{index_name}] at position #[{index}] in %[{table}]."
            )
        else:
            return "Invalid function"
    elif dsl["function_name"] == "drop":
        table = dsl["arguments"][0]
        label = dsl["arguments"][1]
        axis = dsl["arguments"][2]
        if axis == 0 or axis == "index" or axis == "0":
            return f"Drop the row $[{label}] in %[{table}]."
        elif axis == 1 or axis == "columns" or axis == "1":
            return f"Drop the column $[{label}] in %[{table}]."
        else:
            return "Invalid function"
    elif dsl["function_name"] == "assign":
        table = dsl["arguments"][0]
        start_row_index = dsl["arguments"][1]
        end_row_index = dsl["arguments"][2]
        start_column_index = dsl["arguments"][3]
        end_column_index = dsl["arguments"][4]
        values = dsl["arguments"][5]
        string_values = json.dumps(values)
        return f"Assign the values {string_values} to the rows $[{start_row_index}] to $[{end_row_index}] and the columns $[{start_column_index}] to $[{end_column_index}] in %[{table}]."
    elif dsl["function_name"] == "move":
        origin_table = dsl["arguments"][0]
        origin_index = dsl["arguments"][1]
        target_table = dsl["arguments"][2]
        target_index = dsl["arguments"][3]
        axis = dsl["arguments"][4]
        if axis == 0 or axis == "index" or axis == "0":
            return f"Move the row $[{origin_index}] in %[{origin_table}] to %[{target_table}] at position #[{target_index}]."
        elif axis == 1 or axis == "columns" or axis == "1":
            return f"Move the column $[{origin_index}] in %[{origin_table}] to %[{target_table}] at position #[{target_index}]."
        else:
            return "Invalid function"
    elif dsl["function_name"] == "copy":
        origin_table = dsl["arguments"][0]
        origin_index = dsl["arguments"][1]
        target_table = dsl["arguments"][2]
        target_index = dsl["arguments"][3]
        target_label_name = dsl["arguments"][4]
        axis = dsl["arguments"][5]
        if axis == 0 or axis == "index" or axis == "0":
            return f"Copy the row $[{origin_index}] in %[{origin_table}] to %[{target_table}] at position #[{target_index}] with the name $[{target_label_name}]."
        elif axis == 1 or axis == "columns" or axis == "1":
            return f"Copy the column $[{origin_index}] in %[{origin_table}] to %[{target_table}] at position #[{target_index}] with the name $[{target_label_name}]."
        else:
            return "Invalid function"
    elif dsl["function_name"] == "swap":
        table_a = dsl["arguments"][0]
        label_a = dsl["arguments"][1]
        table_b = dsl["arguments"][2]
        label_b = dsl["arguments"][3]
        axis = dsl["arguments"][4]
        if axis == 0 or axis == "index" or axis == "0":
            return f"Swap the row $[{label_a}] in %[{table_a}] with the row $[{label_b}] in %[{table_b}]."
        elif axis == 1 or axis == "columns" or axis == "1":
            return f"Swap the column $[{label_a}] in %[{table_a}] with the column $[{label_b}] in %[{table_b}]."
        else:
            return "Invalid function"
    elif dsl["function_name"] == "merge":
        table_a = dsl["arguments"][0]
        table_b = dsl["arguments"][1]
        on = dsl["arguments"][2]
        how = dsl["arguments"][3]
        axis = dsl["arguments"][4]
        if axis == 0 or axis == "index" or axis == "0":
            return f"Merge %[{table_a}] and %[{table_b}] on $[{on}] with the method *[{how}] along the rows."
        elif axis == 1 or axis == "columns" or axis == "1":
            return f"Merge %[{table_a}] and %[{table_b}] on $[{on}] with the method *[{how}] along the columns."
        else:
            return "Invalid function"
    elif dsl["function_name"] == "concatenate":
        table = dsl["arguments"][0]
        label_a = dsl["arguments"][1]
        label_b = dsl["arguments"][2]
        glue = dsl["arguments"][3]
        new_label = dsl["arguments"][4]
        axis = dsl["arguments"][5]
        if axis == 0 or axis == "index" or axis == "0":
            return f"Concatenate the rows $[{label_a}] and $[{label_b}] in %[{table}] with the glue &[{glue}] as $[{new_label}]."
        elif axis == 1 or axis == "columns" or axis == "1":
            return f"Concatenate the columns $[{label_a}] and $[{label_b}] in %[{table}] with the glue &[{glue}] as $[{new_label}]."
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
        functions = dsl["arguments"][1]
        axis = dsl["arguments"][2]
        if axis == 0 or axis == "index" or axis == "0":
            return f"Aggregate %[{table}] with the functions $[{functions}] along the rows."
        elif axis == 1 or axis == "columns" or axis == "1":
            return f"Aggregate %[{table}] with the functions $[{functions}] along the columns."
        else:
            return "Invalid function"
    elif dsl["function_name"] == "test":
        table = dsl["arguments"][0]
        label_a = dsl["arguments"][1]
        label_b = dsl["arguments"][2]
        strategy = dsl["arguments"][3]
        axis = dsl["arguments"][4]
        if axis == 0 or axis == "index" or axis == "0":
            return f"Test the rows $[{label_a}] and $[{label_b}] in %[{table}] with the strategy *[{strategy}]."
        elif axis == 1 or axis == "columns" or axis == "1":
            return f"Test the columns $[{label_a}] and $[{label_b}] in %[{table}] with the strategy *[{strategy}]."
        else:
            return "Invalid function"
    else:
        return "Invalid function"


def get_summarization(client_id, history):
    summarize_user_prompt = get_history_text(history)

    messages = append_message(summarize_system_prompt, "system", [])
    messages = append_message(summarize_user_prompt, "user", messages)
    summarization = generate_chat_completion(messages)
    messages = append_message(summarization, "assistant", messages)
    log_messages(client_id, "generate_summarization", messages)

    return summarization


def get_step_by_step_plan(client_id, history, summarization, feedback=None):
    if feedback is None:
        plan_user_prompt = plan_user_prompt_template.replace(
            "{USER_INTENTS}", summarization
        ).replace(
            "{INFORMATION}",
            format_information(history["information"], with_table_diff=False),
        )
    else:
        plan_user_prompt = (
            plan_with_feedback_user_prompt.replace("{USER_INTENTS}", summarization)
            .replace(
                "{INFORMATION}",
                format_information(history["information"], with_table_diff=False),
            )
            .replace("{FEEDBACK}", feedback["feedback"])
        )

    messages = append_message(plan_system_prompt, "system", [])
    messages = append_message(plan_user_prompt, "user", messages)
    step_by_step_plan = generate_chat_completion(messages)
    messages = append_message(step_by_step_plan, "assistant", messages)
    log_messages(client_id, "generate_step_by_step_plan", messages)

    return step_by_step_plan


def get_dsls(client_id, history, step_by_step_plan, feedback=None):
    if feedback is None:
        generate_user_prompt = generate_user_prompt_template.replace(
            "{PLAN}", step_by_step_plan
        ).replace(
            "{INFORMATION}",
            format_information(history["information"], with_table_diff=False),
        )
    else:
        generate_user_prompt = (
            generate_with_feedback_user_prompt.replace("{PLAN}", step_by_step_plan)
            .replace(
                "{INFORMATION}",
                format_information(history["information"], with_table_diff=False),
            )
            .replace("{FEEDBACK}", feedback["feedback"])
        )

    messages = append_message(generate_system_prompt, "system", [])
    messages = append_message(generate_user_prompt, "user", messages)
    generated_dsl = generate_chat_completion(messages)
    messages = append_message(generated_dsl, "assistant", messages)
    log_messages(client_id, "generate_dsl", messages)

    dsls = json.loads(generated_dsl)
    return dsls


def verify(client_id, history, summarization, dsls):
    verifier_user_prompt = (
        verifier_user_prompt_template.replace(
            "{INFORMATION}",
            format_information(history["information"], with_table_diff=False),
        )
        .replace("{USER_INTENTS}", summarization)
        .replace("{GENERATED_DSLS}", json.dumps(dsls))
    )
    messages = append_message(verifier_system_prompt, "system", [])
    messages = append_message(verifier_user_prompt, "user", messages)
    feedback = generate_chat_completion(messages)
    messages = append_message(feedback, "assistant", messages)
    log_messages(client_id, "generate_feedback", messages)
    feedback = json.loads(feedback)
    return feedback


def dsl_synthesize(client_id: str) -> str:
    history = get_history(client_id)
    summarization = get_summarization(client_id, history)
    step_by_step_plan = get_step_by_step_plan(client_id, history, summarization)
    dsls = get_dsls(client_id, history, step_by_step_plan)
    feedback = verify(client_id, history, summarization, dsls)

    while feedback["correctness"] == "incorrect":
        step_by_step_plan = get_step_by_step_plan(
            client_id, history, summarization, feedback
        )
        dsls = get_dsls(client_id, history, step_by_step_plan, feedback)
        feedback = verify(client_id, history, summarization, dsls)

    for dsl in dsls:
        dsl["natural_language"] = transfer_to_NL(dsl)
    return dsls
