from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import uuid
import json

from utils.analyze import analyze
from utils.chat import chat
from utils.compile import dsl_compile
from utils.llm import get_client, create_client

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


clients = {}


@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if file.content_type != "text/csv":
        return {"error": "File must be a CSV"}

    file_location = f"files/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"info": f"File '{file.filename}' saved."}


class Chat(BaseModel):
    status: str
    client_id: Optional[str] = Field(None)
    message: str = Field(None)
    sheet_id: Optional[str] = Field(None)
    row_count: Optional[int] = Field(None)
    column_names: Optional[List[str]] = Field(None)
    table_diff: Optional[str] = Field(None)
    user_prompt: Optional[str] = Field(None)


@app.post("/chat")
async def handle_chat(request_body: Chat):
    status = request_body.status
    print(status)
    if status == "init":
        return await simple_chat(request_body)
    if status == "with_demo":
        return await handle_analyze(request_body)
    elif status == "clarification":
        return await handle_response(request_body)
    elif status == "generate_dsl":
        return await handle_generate_dsl(request_body)


class SimpleChat(BaseModel):
    client_id: Optional[str] = Field(None)
    message: str


@app.post("/simple_chat")
async def simple_chat(request_body: SimpleChat):
    client_id = request_body.client_id
    message = request_body.message
    if not client_id:
        client_id, client = create_client()
        client.append_user_message(message)
        response = client.generate_chat_completion()
        client.append_assistant_message(response)
        return_message = {
            "client_id": client_id,
            "history": client.history,
            "response": response,
        }
    else:
        client = get_client(client_id)
        client.append_user_message(message)
        response = client.generate_chat_completion()
        client.append_assistant_message(response)
        return_message = {
            "client_id": client_id,
            "history": client.history,
            "response": response,
        }
    return return_message


class Analyze(BaseModel):
    sheet_id: str
    row_count: int
    column_names: List[str]
    table_diff: str
    user_prompt: str


@app.post("/analyze")
async def handle_analyze(request_body: Analyze):
    sheet_id = request_body.sheet_id
    row_count = request_body.row_count
    column_names = request_body.column_names
    table_diff = request_body.table_diff
    user_prompt = request_body.user_prompt

    client_id, response = analyze(
        sheet_id, row_count, column_names, table_diff, user_prompt
    )
    client = get_client(client_id)

    if response["type"] == "question":
        response_summary = response["summary"]
        response_question = response["question"]
        response_choices = response["choices"]
        return_message = {
            "client_id": client_id,
            "history": client.history,
            "question": response_question,
            "choices": response_choices,
            "type": "question",
            "status": "clarification",
        }
    else:
        response_summary = response["summary"]
        return_message = {
            "client_id": client_id,
            "history": client.history,
            "type": "finish",
            "status": "generate_dsl",
        }
    return return_message


class Response(BaseModel):
    client_id: str
    response: str


@app.post("/response")
async def handle_response(request_body: Response):
    client_id = request_body.client_id
    response = chat(client_id, request_body.response)
    if response["type"] == "question":
        response_question = response["question"]
        response_choices = response["choices"]

        return_message = {
            "client_number": client_id,
            "history": client.history,
            "question": response_question,
            "choices": response_choices,
            "type": "question",
            "status": "clarification",
        }
    elif response["type"] == "finish":
        return_message = {
            "client_number": client_id,
            "history": client.history,
            "type": "finish",
            "status": "generate_dsl",
        }
    return return_message


class GenerateDSL(BaseModel):
    client_id: str


@app.post("/generate_dsl")
async def handle_generate_dsl(request_body: GenerateDSL):
    client_id = request_body.client_id

    response = dsl_compile(client_id)
    return_message = {"dsl": response, "status": "finish"}
    return return_message
