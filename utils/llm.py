import os
import re
import json
from openai import OpenAI


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def append_message(content, role, messages):
    messages.append(
        {
            "role": role,
            "content": content,
        }
    )
    return messages


def generate_chat_completion(messages, model="gpt-4o-mini", special_type=None):
    if special_type:
        if special_type == "json_object":
            response = (
                client.chat.completions.create(
                    messages=messages,
                    model=model,
                    response_format={"type": "json_object"},
                )
                .choices[0]
                .message.content
            )
            invalid_backslash_pattern = r'(?<!\\)(\\(?!["\\/bfnrtu]))'
            response = re.sub(invalid_backslash_pattern, r"\\\\", response)
            json_object_pattern = r'\{(?:[^{}]*|\{(?:[^{}]*|\{[^{}]*\})*\})*\}'
            json_objects = re.findall(json_object_pattern, response)
            response = json.loads(json_objects[0])
        elif special_type == "json_list":
            print("request begin")
            response = (
                client.chat.completions.create(
                    messages=messages,
                    model=model,
                )
                .choices[0]
                .message.content
            )
            print("request end")
            print(response)
            invalid_backslash_pattern = r'(?<!\\)(\\(?!["\\/bfnrtu]))'
            response = re.sub(invalid_backslash_pattern, r"\\\\", response)
            print("1 tag")
            json_list_pattern = r'\[\s*(?:\{[^{}]*\}\s*,?\s*)*\]'

            json_lists = re.findall(json_list_pattern, response)
            print("2 tag")
            response = json.loads(json_lists[0])
            print(response)
    else:
        response = (
            client.chat.completions.create(messages=messages, model=model)
            .choices[0]
            .message.content
        )

    return response
