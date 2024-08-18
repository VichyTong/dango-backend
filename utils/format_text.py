import json
from dsl import function_map


def init_prompt():
    global question_template, answer_template
    global selected_dsl_grammar_template
    global error_message_template
    with open("prompt/template/question.txt") as f:
        question_template = f.read()
    with open("prompt/template/answer.txt") as f:
        answer_template = f.read()
    with open("prompt/synthesize/dsl_grammar_selected.txt", "r") as f:
        selected_dsl_grammar_template = f.read()
    with open("prompt/synthesize/error_message_template.txt", "r") as f:
        error_message_template = f.read()


init_prompt()


def get_history_text(history, is_dump=False, with_table_diff=True):
    if is_dump:
        history = convert_history_to_dumped_text(
            history, with_table_diff=with_table_diff
        )
    else:
        history = convert_history_to_text(history, with_table_diff=with_table_diff)
    return history


def format_information(information, with_table_diff=True):
    result = ""
    for index, item in enumerate(information["sheet_state"]):
        result += item
        if (
            with_table_diff
            and "table_diff" in information
            and index < len(information["table_diff"])
        ):
            result += "\n"
            result += information["table_diff"][index]
    result += "\n"
    result += information["user_prompt"]
    result += "\n"
    return result


def convert_history_to_text(history, with_table_diff=True):
    prompt = format_information(history["information"], with_table_diff)

    question_index = 1
    for pair in history["question_answer_pairs"]:
        question = pair["question"]
        choices = pair["choices"]

        choices_text = ""
        for i, choice in enumerate(choices, start=1):
            choices_text += f"{i}. {choice}\n"

        prompt += "\n"

        question_answer_pair = (
            question_template.replace("{INDEX}", str(question_index))
            .replace("{QUESTION}", question)
            .replace("{CHOICES}", choices_text)
        )
        if "answer" in pair:
            answer = pair["answer"]
            question_answer_pair += answer_template.replace(
                "{INDEX}", str(question_index)
            ).replace("{ANSWER}", answer)

        question_index += 1
        prompt += question_answer_pair
    return prompt


def convert_history_to_dumped_text(history, with_table_diff=True):
    prompt = format_information(history["information"], with_table_diff)
    prompt += "Question & Answering History:\n"

    for pair in history["question_answer_pairs"]:
        question = pair["question"]
        choices = pair["choices"]
        summary = pair["summary"]

        question_answer_pair = "ASSISTANT:\n"
        question_answer_pair += json.dumps(
            {
                "type": "question",
                "summary": summary,
                "question": question,
                "choices": choices,
            },
            indent=4,
        )

        answer = pair["answer"]
        question_answer_pair += "\n\nUSER:\n"
        question_answer_pair += json.dumps({"choice": answer}, indent=4)

        prompt += question_answer_pair
    return prompt


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
        selected_dsl_grammar_template.replace(
            "{TABLE-LEVEL FUNCTIONS}", table_level_text
        )
        .replace("{CLOUMN/ROW-LEVEL FUNCTIONS}", column_row_level_text)
        .replace("{SUMMARIZATION FUNCTIONS}", summarization_text)
        .replace("{STRING OPERATION FUNCTIONS}", string_operation_functions)
        .strip()
    )
