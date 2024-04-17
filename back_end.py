from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import uuid
import json

from utils.analyze import analyze
from utils.chat import chat
from utils.compile import dsl_compile
from utils.llm import get_client

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
        }
    else:
        response_summary = response["summary"]
        return_message = {
            "client_id": client_id,
            "history": client.history,
            "type": "finish",
        }
    return return_message


class Response(BaseModel):
    client_id: str
    response: str


@app.post("/response")
async def handle_response(request_body: Response):
    client_id = request_body.client_id
    return chat(client_id, request_body.response)


class GenerateDSL(BaseModel):
    client_id: str


@app.post("/generate_dsl")
async def handle_generate_dsl(request_body: GenerateDSL):
    client_id = request_body.client_id

    response = dsl_compile(client_id)
    return_message = {"dsl": response}
    return return_message
