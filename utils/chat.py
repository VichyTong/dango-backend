import json

from utils.llm import get_client


def chat(client_id, response):
    client = get_client(client_id)
    client.append_user_message(response)

    response = client.generate_chat_completion()
    client.append_assistant_message(response)
    response = json.loads(response)

    if response["type"] == "question":
        response_question = response["question"]
        response_choices = response["choices"]

        return_message = {
            "client_number": client_id,
            "history": client.history,
            "question": response_question,
            "choices": response_choices,
            "type": "question",
        }
    elif response["type"] == "finish":
        return_message = {
            "client_number": client_id,
            "history": client.history,
            "type": "finish",
        }

    return return_message
