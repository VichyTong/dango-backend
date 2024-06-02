import json

from utils.llm import get_history, append_message, generate_chat_completion


def chat(client_id, response):
    client = get_history(client_id)
    append_message(client_id, response, "user")

    response = generate_chat_completion(client_id)
    append_message(client_id, response, "assistant")
    response = json.loads(response)
    return response