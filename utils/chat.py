import json

from utils.llm import get_client


def chat(client_id, response):
    client = get_client(client_id)
    client.append_user_message(response)

    response = client.generate_chat_completion()
    client.append_assistant_message(response)
    response = json.loads(response)
    return response