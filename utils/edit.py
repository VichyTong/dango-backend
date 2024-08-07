import json

from utils.llm import (
    append_message,
    generate_chat_completion,
)


def init_prompt():
    global dsl_grammar
    global edit_dsl_system_prompt, edit_dsl_user_template
    with open("prompt/synthesize/dsl_grammar.txt", "r") as f:
        dsl_grammar = f.read()
    with open("prompt/edit/edit_dsl_system.txt", "r") as f:
        edit_dsl_system_prompt = f.read().replace("{DSL_GRAMMAR}", dsl_grammar)
    with open("prompt/edit/edit_dsl_user.txt", "r") as f:
        edit_dsl_user_template = f.read()


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
    print(json.dumps(messages, indent=4))
    edited_dsl = generate_chat_completion(messages, special_type="json_object")
    return edited_dsl
