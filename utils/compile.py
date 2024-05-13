import json

from utils.llm import create_client, get_client


def init_prompt():
    global system_prompt
    with open("prompt/compile/system.txt", "r") as f:
        system_prompt = f.read()


init_prompt()


def create_user_prompt(history):
    information = history[1]["content"]
    QAs = ""
    for index in range(2, len(history), 2):
        response = json.loads(history[index]["content"])
        if response["type"] == "finish":
            break
        question = f"Q: {response['question']}\nChoices:\n"
        for i, choice in enumerate(response["choices"]):
            question += f"{i + 1}. {choice}\n"
        answer = history[index + 1]["content"]
        answer = f"A: {answer}\n"
        QAs += f"{question}{answer}\n"
    user_prompt = f"{information}\n{QAs}"
    return user_prompt


def dsl_compile(client_id: str) -> str:
    history = get_client(client_id).history
    user_prompt = create_user_prompt(history)

    _, client = create_client()
    client.append_system_message(system_prompt)
    client.append_user_message(user_prompt)
    print(client.history)
    response = client.generate_chat_completion()
    print(response)
    dsl = json.loads(response)["DSL"]
    return dsl
