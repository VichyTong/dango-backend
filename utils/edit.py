import json

from utils.llm import (
    append_message,
    generate_chat_completion,
)
from utils.convert2NL import transfer_to_NL
from utils.db import get_DSL_functions, update_DSL_functions


def init_prompt():
    global dsl_grammar
    global edit_dsl_system_prompt, edit_dsl_user_template
    global create_dsl_system_prompt, create_dsl_user_template
    with open("prompt/synthesize/dsl_grammar.txt", "r") as f:
        dsl_grammar = f.read()
    with open("prompt/edit/edit_dsl_system.txt", "r") as f:
        edit_dsl_system_prompt = f.read().replace("{DSL_GRAMMAR}", dsl_grammar)
    with open("prompt/edit/edit_dsl_user.txt", "r") as f:
        edit_dsl_user_template = f.read()
    with open("prompt/edit/create_dsl_system.txt", "r") as f:
        create_dsl_system_prompt = f.read().replace("{DSL_GRAMMAR}", dsl_grammar)
    with open("prompt/edit/create_dsl_user.txt", "r") as f:
        create_dsl_user_template = f.read()


init_prompt()


def edit_dsl(client_id, dsl, new_instruction):
    function = dsl.function_name
    arguments = dsl.arguments
    try:
        condition = dsl.condition
        dsl = {
            "function": function,
            "arguments": arguments,
            "condition": condition,
        }
    except AttributeError:
        dsl = {
            "function": function,
            "arguments": arguments,
        }

    edit_dsl_user_prompt = edit_dsl_user_template.replace(
        "{DSL}", json.dumps(dsl, indent=4)
    ).replace("{INSTRUCTIONS}", new_instruction)
    messages = append_message(edit_dsl_system_prompt, "system", [])
    messages = append_message(edit_dsl_user_prompt, "user", messages)
    edited_dsl = generate_chat_completion(messages, special_type="json_object")
    # Apply transfer_to_NL and add natural_language field
    edited_dsl["natural_language"] = transfer_to_NL(edited_dsl)

    dsl_functions = get_DSL_functions(client_id)
    for i, d in enumerate(dsl_functions["program"]):
        if d["function_name"] == function and d["arguments"] == arguments:
            dsl_functions["program"][i] = edited_dsl
            break
    update_DSL_functions(client_id, dsl_functions)
    return edited_dsl


def create_dsl(client_id, new_instruction):
    dsl_functions = get_DSL_functions(client_id)

    create_dsl_user_prompt = create_dsl_user_template.replace(
        "{DSL_LIST}", json.dumps(dsl_functions["program"], indent=4)
    ).replace("{INSTRUCTIONS}", new_instruction)
    messages = append_message(create_dsl_system_prompt, "system", [])
    messages = append_message(create_dsl_user_prompt, "user", messages)
    created_dsl = generate_chat_completion(messages, special_type="json_object")
    # Apply transfer_to_NL and add natural_language field
    created_dsl["natural_language"] = transfer_to_NL(created_dsl)

    dsl_functions["program"].append(created_dsl)
    update_DSL_functions(client_id, dsl_functions)
    return created_dsl
