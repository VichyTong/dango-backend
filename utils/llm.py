import os
from openai import OpenAI


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def append_message(content, role, messages=[]):
    messages.append(
        {
            "role": role,
            "content": content,
        }
    )
    return messages


def generate_chat_completion(messages, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(messages=messages, model=model).choices[0].message.content
    # print("------------------------------INPUTS------------------------------")
    # for item in messages:
    #     print(item["content"])
    # print("------------------------------OUTPUTS------------------------------")
    # print(response)
    return response
