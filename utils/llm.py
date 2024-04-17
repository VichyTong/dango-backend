import os
from openai import OpenAI
import uuid


clients = {}


class OpenAIClient:
    def __init__(self, client_id, api_key=None):
        self.client_id = client_id
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        self.history = []

    def generate_chat_completion(self, model="gpt-3.5-turbo"):
        return (
            self.client.chat.completions.create(messages=self.history, model=model)
            .choices[0]
            .message.content
        )

    def clear_history(self):
        self.history = []

    def append_system_message(self, message):
        self.history.append({"role": "system", "content": message})

    def append_user_message(self, message):
        self.history.append({"role": "user", "content": message})

    def append_assistant_message(self, message):
        self.history.append({"role": "assistant", "content": message})


def create_client():
    client_id = str(uuid.uuid4())
    client = OpenAIClient(client_id, api_key=os.environ.get("OPENAI_API_KEY"))
    clients[client_id] = client
    return client_id, client


def get_client(client_id): 
    return clients.get(client_id)
