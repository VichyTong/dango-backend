import os
from openai import OpenAI
import uuid

from utils.db import create_history, get_history, update_history, clear_history


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def append_message(client_id, message, message_type):
    update_history(client_id, {"role": message_type, "content": message})


def generate_chat_completion(client_id, model="gpt-3.5-turbo"):
    history = get_history(client_id)
    return (
        client.chat.completions.create(messages=history, model=model)
        .choices[0]
        .message.content
    )


def create_client():
    client_id = str(uuid.uuid4())
    create_history(client_id)
    return client_id
