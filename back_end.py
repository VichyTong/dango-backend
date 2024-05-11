from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
    allow_origins=["*"],  # Adjust this to match your frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = {}

UPLOAD_FOLDER = "./files"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    unique_filename = f"{uuid.uuid4()}_{file.filename}"

    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    # Save the file
    try:
        with open(file_path, "wb") as buffer:
            while data := await file.read(1024):
                buffer.write(data)
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {e}")

    return JSONResponse(status_code=200, content={"sheet_id": unique_filename})


@app.post("/modify/{sheet_id}")
async def modify_file(sheet_id: str, file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    file_path = os.path.join(UPLOAD_FOLDER, sheet_id)

    # Replace the file
    try:
        with open(file_path, "wb") as buffer:
            while data := await file.read(1024):
                buffer.write(data)
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"File modification failed: {e}")

    return JSONResponse(
        status_code=200,
        content={"message": "File modified successfully", "sheet_id": sheet_id},
    )


@app.delete("/delete/{sheet_id}")
async def delete_file(sheet_id: str):
    file_path = os.path.join(UPLOAD_FOLDER, sheet_id)

    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Delete the file
    try:
        os.remove(file_path)
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"File deletion failed: {e}")

    return JSONResponse(
        status_code=200, content={"message": "File deleted successfully"}
    )


class Chat(BaseModel):
    status: str
    client_id: Optional[str] = Field(None)
    message: str = Field(None)
    sheet_id: Optional[str] = Field(None)
    row_count: Optional[int] = Field(None)
    column_names: Optional[List[str]] = Field(None)
    table_diff: Optional[str] = Field(None)
    user_prompt: Optional[str] = Field(None)
    response: Optional[str] = Field(None)


@app.post("/chat")
async def handle_chat(request_body: Chat):
    status = request_body.status
    print(status)
    if status == "init":
        return await simple_chat(request_body)
    if status == "analyze":
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
            "status": "init",
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
            "status": "init",
        }
    return return_message


class Analyze(BaseModel):
    sheet_id: str
    row_count: int
    column_names: List[str]
    table_diff: str
    user_prompt: str
    user_choice: str


@app.post("/analyze")
async def handle_analyze(request_body: Analyze):
    sheet_id = request_body.sheet_id
    row_count = request_body.row_count
    column_names = request_body.column_names
    table_diff = request_body.table_diff
    user_prompt = request_body.user_prompt
    user_choice = request_body.user_choice

    client_id, response = analyze(
        sheet_id, row_count, column_names, table_diff, user_prompt, user_choice
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
    client = get_client(client_id)
    user_response = request_body.response
    response = chat(client_id, user_response)
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
