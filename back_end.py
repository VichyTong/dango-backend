from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from llm import OpenAIClient
from pydantic import BaseModel
import os
import uuid
import json

# Initialize FastAPI app
app = FastAPI()

# Allow CORS
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

with open("prompt/clarification.txt", "r") as file:
    clarification_prefix = file.read()

with open("prompt/DSL.txt", "r") as file:
    DSL_prefix = file.read()

clients = {}


class CreateClarification(BaseModel):
    demonstration: str


@app.post("/create_clarification")
async def create_clarification(request_body: CreateClarification):
    demonstration = request_body.demonstration

    if not demonstration:
        raise HTTPException(status_code=400, detail="Demonstration are required")

    client_id = str(uuid.uuid4())
    client = OpenAIClient(client_id, api_key=os.environ.get("OPENAI_API_KEY"))
    clients[client_id] = client

    client.append_system_message(clarification_prefix)
    client.append_user_message(demonstration)

    chat_response = client.generate_chat_completion(client.history)
    chat_response_full = json.loads(chat_response.choices[0].message.content)

    if chat_response_full["type"] == "question":
        chat_response_content = chat_response_full["content"]
        chat_response_choices = chat_response_full["choices"]

        full_text = chat_response_content + "\nChoices:\n"
        for choice in chat_response_choices:
            full_text += choice + "\n"

        client.append_assistant_message(full_text)  # Append response to history

        return_message = {
            "client_number": client.client_id,
            "history": client.history,
            "content": chat_response_content,
            "choices": chat_response_choices,
            "type": "question",
        }
    else:
        message = "Something went wrong.\nMessage:" + chat_response.choices[0].message.content
        raise HTTPException(status_code=500, detail=message)
    return return_message


class ContinueClarification(BaseModel):
    client_number: str
    answer: str
    cancel: bool


@app.post("/continue_clarification")
async def continue_clarification(request_body: ContinueClarification):
    client_number = request_body.client_number
    answer = request_body.answer
    cancel = request_body.cancel

    if not client_number:
        raise HTTPException(status_code=400, detail="Client number is required")

    if not answer and not cancel:
        raise HTTPException(status_code=400, detail="Answer or cancel is required")

    if client_number not in clients:
        raise HTTPException(status_code=400, detail="Client number is not found")

    client = clients[client_number]

    if cancel:
        client.clear_history()
        clients.delete(client_number)
        return_message = {
            "client_number": client.client_id,
            "history": client.history,
            "response": "Clarification is canceled",
            "type": "finish",
        }
        return return_message

    client.append_user_message(answer)

    chat_response = client.generate_chat_completion(client.history)
    chat_response_full = json.loads(chat_response.choices[0].message.content)
    if chat_response_full["type"] == "question":
        chat_response_content = chat_response_full["content"]
        chat_response_choices = chat_response_full["choices"]

        full_text = chat_response_content + "\nChoices:\n"
        for choice in chat_response_choices:
            full_text += choice + "\n"

        client.append_assistant_message(full_text)  # Append response to history

        return_message = {
            "client_number": client.client_id,
            "history": client.history,
            "content": chat_response_content,
            "choices": chat_response_choices,
            "type": "question",
        }
    elif chat_response_full["type"] == "finish":
        return_message = {
            "client_number": client.client_id,
            "history": client.history,
            "type": "finish",
        }

    return return_message


class GenerateDSL(BaseModel):
    history: list


@app.post("/generate_dsl")
async def generate_dsl(request_body: GenerateDSL):
    history = request_body.history

    if not history:
        raise HTTPException(status_code=400, detail="History is required")

    client_id = str(uuid.uuid4())
    client = OpenAIClient(client_id, api_key=os.environ.get("OPENAI_API_KEY"))
    clients[client_id] = client

    client.append_system_message(DSL_prefix)
    client.append_user_message("History:\n" + json.dumps(history))

    chat_response = client.generate_chat_completion(client.history)
    chat_response_content = json.loads(chat_response.choices[0].message.content)

    client.append_assistant_message(chat_response_content)

    return_message = {
        "client_number": client.client_id,
        "response": chat_response_content["DSL"],
        "history": client.history,
    }
    return return_message
