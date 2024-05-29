from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import uuid
import json
import aiofiles
import pandas as pd

from utils.analyze import analyze, multi_analyze
from utils.chat import chat
from utils.compile import dsl_compile
from utils.llm import get_client, create_client
from utils.execute import execute_dsl

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


@app.post("/login/")
async def login():
    client_id, client = create_client()
    return JSONResponse(status_code=200, content={"client_id": client_id})


@app.post("/upload/")
async def upload_file(client_id: str = Form(...), file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, content={"message": "Unsupported file type"}
        )
    sheet_id = file.filename
    unique_filename = (
        f"{client_id}_{sheet_id.split('.')[0]}_v0_{sheet_id.split('.')[1]}"
    )

    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    # Save the file
    try:
        async with aiofiles.open(file_path, "wb") as buffer:
            while data := await file.read(1024):
                await buffer.write(data)
    except IOError as e:
        raise HTTPException(
            status_code=500, content={"message": f"File upload failed: {e}"}
        )

    return JSONResponse(
        status_code=200, content={"message": f"{file.filename} uploaded successfully"}
    )


class FileExists(BaseModel):
    client_id: str
    file_name: str
    version: Optional[int] = Field(0)


@app.post("/is_file_exists/")
async def is_file_exists(request_body: FileExists):
    client_id = request_body.client_id
    file_name = request_body.file_name
    version = str(request_body.version)
    print(client_id)
    print(file_name)
    print(version)
    unique_filename = (
        f"{client_id}_{file_name.split('.')[0]}_v{version}_{file_name.split('.')[1]}"
    )
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    if not os.path.exists(file_path):
        return JSONResponse(status_code=200, content={"message": "NO"})
    return JSONResponse(status_code=200, content={"message": "YES"})


@app.delete("/delete/")
async def delete_file(
    client_id: str = Form(...),
    sheet_id: str = Form(...),
    version: Optional[int] = Form(0),
):
    version = str(version)
    unique_filename = (
        f"{client_id}_{sheet_id.split('.')[0]}_v{version}_{sheet_id.split('.')[1]}"
    )
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, content={"message": "File not found"})

    # Delete the file
    try:
        os.remove(file_path)
    except IOError as e:
        raise HTTPException(
            status_code=500, content={"message": f"File deletion failed: {e}"}
        )

    return JSONResponse(
        status_code=200, content={"message": f"{sheet_id} deleted successfully"}
    )


@app.get("/get/")
async def get_file(
    client_id: str = Form(...),
    sheet_id: str = Form(...),
    version: Optional[int] = Form(0),
):
    version = str(version)
    unique_filename = (
        f"{client_id}_{sheet_id.split('.')[0]}_v{version}_{sheet_id.split('.')[1]}"
    )
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, content={"message": "File not found"})

    # return the file
    return FileResponse(file_path)


class TableInfo(BaseModel):
    sheet_id: str
    row_names: List[str]
    column_names: List[str]
    table_diff: str


class MultiAnalyze(BaseModel):
    client_id: str
    table_list: List[TableInfo]
    user_prompt: str


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
    table_list: Optional[List[TableInfo]] = Field(None)


@app.post("/chat")
async def handle_chat(request_body: Chat):
    status = request_body.status
    print(status)
    if status == "init":
        return await simple_chat(request_body)
    if status == "analyze":
        return await handle_analyze(request_body)
    if status == "multi_analyze":
        return await handle_multi_analyze(request_body)
    if status == "clarification":
        return await handle_response(request_body)
    if status == "generate_dsl":
        return await handle_generate_dsl(request_body)


class SimpleChat(BaseModel):
    client_id: Optional[str] = Field(None)
    message: str


@app.post("/simple_chat")
async def simple_chat(request_body: SimpleChat):
    client_id = request_body.client_id
    message = request_body.message

    if not client_id:
        return JSONResponse(
            status_code=400, content={"message": "Client ID is required"}
        )

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
    client_id: str
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
    client_id = request_body.client_id

    file_path = os.path.join(UPLOAD_FOLDER, f"{client_id}_{sheet_id}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    df = pd.read_csv(file_path)
    if "Unnamed: 0" not in df.columns:
        is_index_table = True

    response = analyze(
        client_id,
        sheet_id,
        row_count,
        column_names,
        table_diff,
        user_prompt,
        is_index_table,
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


@app.post("/multi_analyze")
async def handle_multi_analyze(request_body: MultiAnalyze):
    client_id = request_body.client_id
    table_list = request_body.table_list
    user_prompt = request_body.user_prompt

    processed_tables = []
    for table in table_list:
        sheet_id = table.sheet_id
        file_path = os.path.join(UPLOAD_FOLDER, f"{client_id}_{sheet_id}")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        df = pd.read_csv(file_path)
        if "Unnamed: 0" not in df.columns:
            is_index_table = True
        else:
            is_index_table = False
        processed_table = {
            "sheet_id": sheet_id,
            "row_names": table.row_names,
            "column_names": table.column_names,
            "table_diff": table.table_diff,
            "is_index_table": is_index_table,
        }
        processed_tables.append(processed_table)
    print(processed_tables)
    response = multi_analyze(client_id, processed_tables, user_prompt)
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


class ExecuteDSL(BaseModel):
    client_id: str
    sheet_id: Optional[str]
    dsl: str
    arguments: List[str]


@app.post("/execute_dsl")
async def handle_execute_dsl(request_body: ExecuteDSL):
    client_id = request_body.client_id
    dsl = request_body.dsl
    arguments = request_body.arguments
    sheet_id = arguments[0]

    print(f"client_id: {client_id}")
    print(f"sheet_id: {sheet_id}")
    print(f"dsl: {dsl}")
    print(f"arguments: {arguments}")

    file_path = os.path.join(UPLOAD_FOLDER, f"{client_id}_{sheet_id}")
    print(file_path)
    if not os.path.exists(file_path):
        print("File not found")
        raise HTTPException(status_code=404, detail="File not found")

    sheet = pd.read_csv(file_path)
    flag = False
    if "Unnamed: 0" in sheet.columns:
        flag = True
        sheet = pd.read_csv(file_path, index_col=0)

    new_sheet = execute_dsl(sheet, dsl, arguments[1:])
    print(new_sheet)

    # Convert the DataFrame to JSON and return it
    json_result = new_sheet.to_json(orient="records")
    return JSONResponse(content=json_result)
