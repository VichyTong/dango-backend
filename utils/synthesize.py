import json
import re

from utils.llm import (
    append_message,
    generate_chat_completion,
)
from utils.db import get_history, get_all_sheets, get_sheet
from utils.log import log_messages
from utils.format_text import get_history_text, format_information
from utils.verify_syntax import validate_dsls_format, validate_dsls_functions
from utils.convert2NL import transfer_to_NL
from dsl import function_map


def init_prompt():
    global dsl_grammar, selected_dsl_grammar_template
    global summarize_system_prompt
    global plan_system_prompt, plan_user_prompt_template
    global generate_system_prompt_template, generate_user_prompt_template
    global verifier_semantic_system_prompt, verifier_semantic_user_prompt_template
    global error_message_template
    global plan_with_error_message_system_prompt, plan_with_error_message_user_prompt_template
    global generate_with_error_message_system_prompt, generate_with_error_message_user_prompt_template
    global add_information_system_prompt, add_information_user_prompt_template
    global boolean_indexing_system_prompt, boolean_indexing_user_prompt_template
    with open("prompt/synthesize/dsl_grammar.txt", "r") as f:
        dsl_grammar = f.read()
    with open("prompt/synthesize/dsl_grammar_selected.txt", "r") as f:
        selected_dsl_grammar_template = f.read()
    with open("prompt/synthesize/summarize_system.txt", "r") as f:
        summarize_system_prompt = f.read()
    with open("prompt/synthesize/plan_system.txt", "r") as f:
        plan_system_prompt = f.read().replace("{DSL_GRAMMAR}", dsl_grammar)
    with open("prompt/synthesize/plan_user.txt", "r") as f:
        plan_user_prompt_template = f.read()
    with open("prompt/synthesize/generate_system.txt", "r") as f:
        generate_system_prompt_template = f.read().replace("{DSL_GRAMMAR}", dsl_grammar)
    with open("prompt/synthesize/generate_user.txt", "r") as f:
        generate_user_prompt_template = f.read()
    with open("prompt/synthesize/verifier_system.txt", "r") as f:
        verifier_semantic_system_prompt = f.read().replace("{DSL_GRAMMAR}", dsl_grammar)
    with open("prompt/synthesize/verifier_user.txt", "r") as f:
        verifier_semantic_user_prompt_template = f.read()
    with open("prompt/synthesize/error_message_template.txt", "r") as f:
        error_message_template = f.read()
    with open("prompt/synthesize/plan_with_error_message_system.txt", "r") as f:
        plan_with_error_message_system_prompt = f.read()
    with open("prompt/synthesize/plan_with_error_message_user.txt", "r") as f:
        plan_with_error_message_user_prompt_template = f.read()
    with open("prompt/synthesize/generate_with_error_message_system.txt", "r") as f:
        generate_with_error_message_system_prompt = f.read()
    with open("prompt/synthesize/generate_with_error_message_user.txt", "r") as f:
        generate_with_error_message_user_prompt_template = f.read()
    with open("prompt/synthesize/add_information_system.txt", "r") as f:
        add_information_system_prompt = f.read()
    with open("prompt/synthesize/add_information_user.txt", "r") as f:
        add_information_user_prompt_template = f.read()
    with open("prompt/synthesize/boolean_indexing_system.txt", "r") as f:
        boolean_indexing_system_prompt = f.read()
    with open("prompt/synthesize/boolean_indexing_user.txt", "r") as f:
        boolean_indexing_user_prompt_template = f.read()


init_prompt()


def get_summarization(client_id, history):
    summarize_user_prompt = get_history_text(history)

    messages = append_message(summarize_system_prompt, "system", [])
    messages = append_message(summarize_user_prompt, "user", messages)
    summarization = generate_chat_completion(messages)
    messages = append_message(summarization, "assistant", messages)
    log_messages(client_id, "generate_summarization", messages)

    return summarization


def add_more_information(client_id, plan, information):
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

    messages = append_message(add_information_system_prompt, "system", [])
    messages = append_message(
        add_information_user_prompt_template.replace(
            "{INFORMATION}", information
        ).replace("{PLAN}", plan),
        "user",
        messages,
    )

    response = generate_chat_completion(messages, special_type="json_list")
    messages = append_message(response, "assistant", messages)
    log_messages(client_id, "add_information", messages)

    result = ""
    for item in response:
        table_name = item["table_name"]
        label_name = item["label_name"]
        name, version = split_sheet_name(table_name)
        data = get_sheet(client_id, name, version)
        result += f'\n3 Examples of "{label_name}" of {table_name}:\n'
        for index, keys in enumerate(data[label_name]):
            if index == 2:
                result += f'"{data[label_name][keys]}"\n\n'
                break
            result += f'"{data[label_name][keys]}", '
    return result


def format_error_message(error_list):
    error_message = "ERROR_LIST:\n"
    for index, error in enumerate(error_list, start=1):
        if "function_name" in error:
            error_message += (
                error_message_template.replace("{INDEX}", str(index))
                .replace("{ERROR_TYPE}", error["error_type"])
                .replace("{FUNCTION_NAME}", error["function_name"])
                .replace("{MESSAGE}", error["error_message"])
            )
        else:
            error_message += (
                error_message_template.replace("{INDEX}", str(index))
                .replace("{ERROR_TYPE}", error["error_type"])
                .replace("{MESSAGE}", error["error_message"])
            )
    return error_message


def format_selected_dsl_grammar(function_list):
    table_level_functions = set()
    column_row_level_functions = set()
    string_operation_functions = set()
    summarization_functions = set()

    for function_name in function_list:
        if function_name in function_map:
            function_class = function_map[function_name]()
            function_type = function_class.function_type
            function_definition = function_class.definition()
            print(function_definition)

            if function_type == "table":
                table_level_functions.add(function_definition)
            elif function_type == "column_row":
                column_row_level_functions.add(function_definition)
            elif function_type == "summarization":
                summarization_functions.add(function_definition)
            elif function_type == "string_operation":
                string_operation_functions.add(function_definition)

    def format_definition_set(definition_set, prefix):
        if len(definition_set) == 0:
            return ""
        text = prefix
        for index, definition in enumerate(definition_set, start=1):
            text += f"{index}. {definition}\n\n"
        return text

    table_level_text = format_definition_set(
        table_level_functions, "### Table-level Functions\n\n"
    )
    column_row_level_text = format_definition_set(
        column_row_level_functions, "### Column/Row-level Functions\n\n"
    )
    summarization_text = format_definition_set(
        summarization_functions, "### Summarization Functions\n\n"
    )
    string_operation_functions = format_definition_set(
        string_operation_functions, "### String Operation Functions\n\n"
    )

    return (
        selected_dsl_grammar_template.replace("{TABLE-LEVEL FUNCTIONS}", table_level_text)
        .replace("{CLOUMN/ROW-LEVEL FUNCTIONS}", column_row_level_text)
        .replace("{SUMMARIZATION FUNCTIONS}", summarization_text)
        .replace("{STRING OPERATION FUNCTIONS}", string_operation_functions)
        .strip()
    )


def get_step_by_step_plan(
    client_id, history, summarization, error_list=[], last_plan=None
):
    if len(error_list) == 0:
        plan_user_prompt = plan_user_prompt_template.replace(
            "{USER_INTENTS}", summarization
        ).replace(
            "{INFORMATION}",
            format_information(history["information"], with_table_diff=False),
        )
        messages = append_message(plan_system_prompt, "system", [])
    else:
        plan_user_prompt = (
            plan_with_error_message_user_prompt_template.replace(
                "{USER_INTENTS}", summarization
            )
            .replace(
                "{INFORMATION}",
                format_information(history["information"], with_table_diff=False),
            )
            .replace("{ERROR_MESSAGE}", format_error_message(error_list))
            .replace("{PLAN}", last_plan)
        )
        messages = append_message(plan_with_error_message_system_prompt, "system", [])

    messages = append_message(plan_user_prompt, "user", messages)
    step_by_step_plan = generate_chat_completion(messages, special_type="json_list")
    print(json.dumps(step_by_step_plan, indent=4))
    messages = append_message(step_by_step_plan, "assistant", messages)

    step_by_step_plan_string = "Step-by-step Plan:\n"
    for index, item in enumerate(step_by_step_plan, start=1):
        step_by_step_plan_string += (
            f"{index}: {item['description']} ({item['function']} function)\n"
        )

    function_list = [
        "format",
        "split",
    ]
    for item in step_by_step_plan:
        if item["function"] in function_list:
            step_by_step_plan_string += add_more_information(
                client_id,
                item["description"],
                format_information(history["information"], with_table_diff=False),
            )

    log_messages(client_id, "generate_step_by_step_plan", messages)
    return step_by_step_plan, step_by_step_plan_string


def get_dsls(
    client_id,
    history,
    step_by_step_plan,
    step_by_step_plan_string,
    error_list=[],
    last_dsl=None,
):
    funtion_list = []
    print(step_by_step_plan)
    for step in step_by_step_plan:
        funtion_list.append(step["function"])

    if len(error_list) == 0:
        generate_user_prompt = generate_user_prompt_template.replace(
            "{PLAN}", step_by_step_plan_string
        ).replace(
            "{INFORMATION}",
            format_information(history["information"], with_table_diff=False),
        )
        generate_system_prompt = generate_system_prompt_template.replace(
            "{SELECTED_DSL_GRAMMAR}", format_selected_dsl_grammar(funtion_list)
        )
        messages = append_message(generate_system_prompt, "system", [])
    else:
        generate_user_prompt = (
            generate_with_error_message_user_prompt_template.replace(
                "{PLAN}", step_by_step_plan_string
            )
            .replace(
                "{INFORMATION}",
                format_information(history["information"], with_table_diff=False),
            )
            .replace("{ERROR_MESSAGE}", format_error_message(error_list))
            .replace("{DSL}", json.dumps(last_dsl, indent=4))
        )
        messages = append_message(
            generate_with_error_message_system_prompt, "system", []
        )

    messages = append_message(generate_user_prompt, "user", messages)
    generated_dsl = generate_chat_completion(messages, special_type="json_list")
    print(json.dumps(generated_dsl, indent=4))
    messages = append_message(generated_dsl, "assistant", messages)
    log_messages(client_id, "generate_dsl", messages)
    return generated_dsl


def verify_syntax(client_id, dsls, error_list):
    all_sheets = get_all_sheets(client_id)
    validate_dsls_format(dsls)
    validate_dsls_functions(dsls, all_sheets, error_list)
    return True


def verify_semantics(client_id, history, summarization, dsls):
    verifier_semantic_user_prompt = (
        verifier_semantic_user_prompt_template.replace(
            "{INFORMATION}",
            format_information(history["information"], with_table_diff=False),
        )
        .replace("{USER_INTENTS}", summarization)
        .replace("{GENERATED_DSLS}", json.dumps(dsls, indent=4))
    )
    messages = append_message(verifier_semantic_system_prompt, "system", [])
    messages = append_message(verifier_semantic_user_prompt, "user", messages)
    feedback = json.loads(generate_chat_completion(messages))
    messages = append_message(feedback, "assistant", messages)
    log_messages(client_id, "generate_feedback", messages)
    return feedback


def verify(client_id, history, summarization, dsls):
    error_list = []
    print(f"Step 0:\n{json.dumps(error_list, indent=4)}")
    print("syntax_start")
    verify_syntax(client_id, dsls, error_list)
    print("syntax_end")
    print(f"Step 1:\n{json.dumps(error_list, indent=4)}")
    print("semantic_start")
    feedback = verify_semantics(client_id, history, summarization, dsls)
    print("semantic_end")
    print(f"Step 2:\n{json.dumps(error_list, indent=4)}")
    if feedback["correctness"] == "No":
        error_list.append(feedback["feedback"]["error"])
    return error_list


def fill_condition(client_id, dsls):
    def extract_to_dict(s):
        type_pattern = r"Type: (\w+)"
        function_pattern = r"```(.*?)```"

        type_match = re.search(type_pattern, s, re.DOTALL)
        function_match = re.search(function_pattern, s, re.DOTALL)

        result = {
            "type": type_match.group(1) if type_match else None,
            "function": function_match.group(1).strip() if function_match else None,
        }
        return result

    for dsl in dsls:
        if "condition" in dsl:
            boolean_indexing_user_prompt = (
                boolean_indexing_user_prompt_template.replace(
                    "CONDITION", dsl["condition"]
                )
            )
            messages = append_message(boolean_indexing_system_prompt, "system", [])
            messages = append_message(boolean_indexing_user_prompt, "user", messages)
            response = generate_chat_completion(messages)
            messages = append_message(response, "assistant", messages)
            log_messages(client_id, "generate_boolean_indexing", messages)
            response = extract_to_dict(response)
            dsl["type"] = response["type"]
            dsl["function"] = response["function"]
    return dsls


def dsl_synthesize(client_id: str) -> str:
    history = get_history(client_id)
    summarization = get_summarization(client_id, history)
    step_by_step_plan, step_by_step_plan_string = get_step_by_step_plan(
        client_id, history, summarization
    )
    dsls = get_dsls(client_id, history, step_by_step_plan, step_by_step_plan_string)
    error_list = verify(client_id, history, summarization, dsls)
    print(error_list)
    dsls = fill_condition(client_id, dsls)
    print("1 run")
    count = 1
    while len(error_list) > 0 and count < 5:
        count += 1
        step_by_step_plan, step_by_step_plan_string = get_step_by_step_plan(
            client_id, history, summarization, error_list, step_by_step_plan_string
        )
        dsls = get_dsls(
            client_id,
            history,
            step_by_step_plan,
            step_by_step_plan_string,
            error_list,
            dsls,
        )
        error_list = verify(client_id, history, summarization, dsls)
        dsls = fill_condition(client_id, dsls)
        print(f"{count} run")
    print(f"Total count: {count}")
    for dsl in dsls:
        dsl["natural_language"] = transfer_to_NL(dsl)
    return dsls
