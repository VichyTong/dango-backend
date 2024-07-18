import os
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


def generate_chat_completion(messages, model="gpt-3.5-turbo", json=False):
    response = client.chat.completions.create(messages=messages, model=model).choices[0].message.content
    if json:
        response = response.replace('\\', '\\\\')
    return response
