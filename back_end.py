from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from io import StringIO
import os
import uuid
import json
import aiofiles
import pandas as pd

from utils.simple_analyze import simple_analyze
from utils.analyze import analyze, multi_analyze
from utils.chat import chat
from utils.compile import dsl_compile
from utils.llm import (
    get_history,
    create_client,
    update_history,
    append_message,
    generate_chat_completion,
)
from utils.db import (
    upload_sheet,
    get_sheet,
    delete_sheet,
    is_sheet_exists,
    get_all_sheets,
    find_next_version,
)
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
    client_id = create_client()
    return JSONResponse(status_code=200, content={"client_id": client_id})


@app.post("/upload/")
async def upload_file(client_id: str = Form(...), file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, content={"message": "Unsupported file type"}
        )
    sheet_id = file.filename
    version = 0
    # read the sheet to json
    data = await file.read()
    data = data.decode("utf-8")
    csv_data = StringIO(data)
    data = pd.read_csv(csv_data)
    data = data.to_json(orient="records")
    data = json.loads(data)
    upload_sheet(client_id, sheet_id, 0, data)

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

    is_exists = is_sheet_exists(client_id, file_name, version)

    if not is_exists:
        return JSONResponse(status_code=200, content={"message": "NO"})
    return JSONResponse(status_code=200, content={"message": "YES"})


@app.delete("/delete/")
async def delete_file(
    client_id: str = Form(...),
    sheet_id: str = Form(...),
    version: Optional[int] = Form(0),
):
    # Check if file exists
    if not is_sheet_exists(client_id, sheet_id, version):
        raise HTTPException(status_code=404, content={"message": "File not found"})

    # Delete the file
    delete_sheet(client_id, sheet_id, version)

    return JSONResponse(
        status_code=200, content={"message": f"{sheet_id} deleted successfully"}
    )


@app.get("/get/")
async def get_file(
    client_id: str = Form(...),
    sheet_id: str = Form(...),
    version: Optional[int] = Form(0),
):
    # Check if file exists
    if not is_sheet_exists(client_id, sheet_id, version):
        raise HTTPException(status_code=404, content={"message": "File not found"})

    sheet = json.dumps(get_sheet(client_id, sheet_id, version), indent=4)
    # return the file
    return JSONResponse(
        status_code=200,
        content={"data": sheet},
    )


def get_sheet_info(client_id, sheet_id, version):
    sheet = get_sheet(client_id, sheet_id, version)
    df = pd.DataFrame(sheet)
    output = {}
    if "Unnamed: 0" not in df.columns:
        output["is_index_table"] = True
    else:
        output["is_index_table"] = False

    output["column_names"] = df.columns.tolist()
    output["row_names"] = df.index.tolist()

    return output


class TableInfo(BaseModel):
    sheet_id: str
    version: Optional[int] = Field(0)
    table_diff: Optional[str] = None


class MultiAnalyze(BaseModel):
    client_id: str
    table_list: Optional[List[TableInfo]] = None
    message: str


class Chat(BaseModel):
    status: str
    client_id: Optional[str] = Field(None)
    message: str = Field(None)
    sheet_id: Optional[str] = Field(None)
    version: Optional[int] = Field(0)
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
        return await handle_multi_analyze(request_body)
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

    history = get_history(client_id)
    append_message(client_id, message, "user")
    response = generate_chat_completion(client_id)
    append_message(client_id, response, "assistant")
    return_message = {
        "client_id": client_id,
        "history": history,
        "response": response,
        "status": "init",
    }

    return return_message


class Analyze(BaseModel):
    client_id: str
    sheet_id: str
    version: Optional[int] = Field(0)
    row_count: int
    column_names: List[str]
    table_diff: str
    user_prompt: str


@app.post("/analyze")
async def handle_analyze(request_body: Analyze):
    client_id = request_body.client_id
    sheet_id = request_body.sheet_id
    version = request_body.version
    row_count = request_body.row_count
    column_names = request_body.column_names
    table_diff = request_body.table_diff
    user_prompt = request_body.user_prompt

    sheet_info = get_sheet_info(client_id, sheet_id, version)

    response = analyze(
        client_id,
        sheet_id,
        version,
        len(sheet_info["row_names"]),
        sheet_info["column_names"],
        table_diff,
        user_prompt,
        sheet_info["is_index_table"],
    )
    history = get_history(client_id)

    if response["type"] == "question":
        response_summary = response["summary"]
        response_question = response["question"]
        response_choices = response["choices"]
        return_message = {
            "client_id": client_id,
            "history": history,
            "question": response_question,
            "choices": response_choices,
            "type": "question",
            "status": "clarification",
        }
    else:
        response_summary = response["summary"]
        return_message = {
            "client_id": client_id,
            "history": history,
            "type": "finish",
            "status": "generate_dsl",
        }
    return return_message


@app.post("/multi_analyze")
async def handle_multi_analyze(request_body: MultiAnalyze):
    client_id = request_body.client_id
    table_list = request_body.table_list
    user_prompt = request_body.message

    if not table_list:
        table_list = []
        sheets = get_all_sheets(client_id)
        for sheet in sheets:
            sheet_id = sheet[0]
            version = sheet[1]
            table_diff = None
            table_info = TableInfo(
                sheet_id=sheet_id, version=version, table_diff=table_diff
            )
            table_list.append(table_info)

    print(">>> multi_analyze Table List:")
    print(table_list)

    processed_tables = []
    for table in table_list:
        sheet_id = table.sheet_id
        version = table.version
        sheet_info = get_sheet_info(client_id, sheet_id, version)

        processed_table = {
            "sheet_id": sheet_id,
            "version": version,
            "row_names": sheet_info["row_names"],
            "column_names": sheet_info["column_names"],
            "table_diff": table.table_diff,
            "is_index_table": sheet_info["is_index_table"],
        }
        processed_tables.append(processed_table)
    print(processed_tables)
    response = multi_analyze(client_id, processed_tables, user_prompt)
    history = get_history(client_id)

    if response["type"] == "question":
        response_summary = response["summary"]
        response_question = response["question"]
        response_choices = response["choices"]
        return_message = {
            "client_id": client_id,
            "history": history,
            "question": response_question,
            "choices": response_choices,
            "type": "question",
            "status": "clarification",
        }
    else:
        response_summary = response["summary"]
        return_message = {
            "client_id": client_id,
            "history": history,
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
    history = get_history(client_id)
    user_response = request_body.response
    response = chat(client_id, user_response)
    print("Response:")
    print(response)
    if response["type"] == "question":
        response_question = response["question"]
        response_choices = response["choices"]

        return_message = {
            "client_id": client_id,
            "history": history,
            "question": response_question,
            "choices": response_choices,
            "type": "question",
            "status": "clarification",
        }
    elif response["type"] == "finish":
        return_message = {
            "client_id": client_id,
            "history": history,
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

    print(f"client_id: {client_id}")
    print(f"dsl: {dsl}")
    print(f"arguments: {arguments}")

    def get_sheet_info(sheet_name):
        sheet_id = "_".join(sheet_name.split("_")[:-1]) + ".csv"
        version = int(sheet_name.split("_")[-1][1:].split(".csv")[0])
        sheet_data = get_sheet(client_id, sheet_id, version)
        sheet = pd.DataFrame(sheet_data)
        flag = False
        if "Unnamed: 0" in sheet.columns:
            flag = True
            sheet = pd.DataFrame(sheet_data, index_col=0)
        return sheet_id, sheet

    single_table_function_list = [
        "drop",
        "merge",
        "split",
        "transpose",
        "aggregate",
    ]
    double_table_function_list = [
        "move",
        "copy",
    ]

    if dsl in single_table_function_list:
        sheet_id, sheet = get_sheet_info(arguments[0])
        new_sheet = execute_dsl(sheet, dsl, arguments[1:])
        new_data = new_sheet.to_json(orient="records")
        new_version = find_next_version(client_id, sheet_id)
        upload_sheet(
            client_id, sheet_id, new_version, new_sheet.to_dict(orient="records")
        )
        return [
            {
                "sheet_id": sheet_id,
                "version": new_version,
                "data": new_data,
            }
        ]
    elif dsl in double_table_function_list:
        sheet_id, sheet = get_sheet_info(arguments[0])
        target_sheet_id, target_sheet = get_sheet_info(arguments[2])
        new_sheet, new_target_sheet = execute_dsl(
            sheet, dsl, arguments[1] + arguments[3:], target_sheet=target_sheet
        )
        new_data = new_sheet.to_json(orient="records")
        new_target_data = new_target_sheet.to_json(orient="records")
        new_version = find_next_version(client_id, sheet_id)
        new_target_version = find_next_version(client_id, target_sheet_id)
        upload_sheet(
            client_id, sheet_id, new_version, new_sheet.to_dict(orient="records")
        )
        upload_sheet(
            client_id,
            target_sheet_id,
            new_target_version,
            new_target_sheet.to_dict(orient="records"),
        )
        return [
            {
                "sheet_id": sheet_id,
                "version": new_version,
                "data": new_data,
            },
            {
                "sheet_id": target_sheet_id,
                "version": new_target_version,
                "data": new_target_data,
            },
        ]
    else:
        return "Invalid function"
