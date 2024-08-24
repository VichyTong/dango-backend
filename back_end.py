from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from io import StringIO
import json
import pandas as pd
import time


from utils.analyze import multi_analyze, followup
from utils.synthesize import dsl_synthesize
from utils.db import (
    create_client,
    upload_sheet,
    get_sheet,
    delete_sheet,
    is_sheet_exists,
    get_all_sheets,
    update_client_start_timestamp,
    update_client_end_timestamp,
    get_client_statistics,
)
from utils.execute_program import execute_dsl_list
from utils.dependency import DependenciesManager
from utils.edit import edit_dsl
from config.config import config


app = FastAPI()

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DependenciesManager = DependenciesManager()


@app.post("/login/")
async def login():
    client_id = create_client()
    print(f"Client {client_id} created")
    update_client_start_timestamp(client_id, str(time.time()))
    return JSONResponse(status_code=200, content={"client_id": client_id})


@app.get("/get_statistics/")
async def get_statistics(client_id: str):
    statistics = get_client_statistics(client_id)
    return JSONResponse(status_code=200, content=statistics)


@app.post("/upload/")
async def upload_file(client_id: str = Form(...), file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, content={"message": "Unsupported file type"}
        )
    sheet_id = file.filename

    data = await file.read()
    data = data.decode("utf-8")
    csv_data = StringIO(data)
    data = pd.read_csv(csv_data)

    # Convert the index to string
    data.index = [str(i) for i in range(1, len(data) + 1)]
    data = data.to_dict()

    version = 0
    upload_sheet(client_id, sheet_id, version, data)

    update_client_end_timestamp(client_id, str(time.time()))
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

    is_exists = is_sheet_exists(client_id, file_name, version)

    update_client_end_timestamp(client_id, str(time.time()))
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

    update_client_end_timestamp(client_id, str(time.time()))
    return JSONResponse(
        status_code=200, content={"message": f"{sheet_id} deleted successfully"}
    )


@app.get("/get/")
async def get_file(
    client_id: str = Form(...),
    sheet_id: str = Form(...),
    version: Optional[int] = Form(0),
):
    if not is_sheet_exists(client_id, sheet_id, version):
        raise HTTPException(status_code=404, content={"message": "File not found"})

    sheet = json.dumps(get_sheet(client_id, sheet_id, version), indent=4)

    update_client_end_timestamp(client_id, str(time.time()))
    return JSONResponse(
        status_code=200,
        content={"data": sheet},
    )


def get_sheet_info(client_id, sheet_id, version):
    sheet = get_sheet(client_id, sheet_id, version)
    df = pd.DataFrame(sheet)
    output = {}
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
    if status == "init":
        return await handle_multi_analyze(request_body)
    if status == "multi_analyze":
        return await handle_multi_analyze(request_body)
    if status == "clarification":
        return await handle_response(request_body)
    if status == "generate_dsl":
        return await handle_generate_dsl(request_body)


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
        }
        processed_tables.append(processed_table)

    response = multi_analyze(client_id, processed_tables, user_prompt)
    if response["type"] == "question":
        response_question = response["question"]
        response_choices = response["choices"]
        return_message = {
            "client_id": client_id,
            "question": response_question,
            "choices": response_choices,
            "type": "question",
            "status": "clarification",
        }
    elif response["type"] == "finish":
        return_message = {
            "client_id": client_id,
            "type": "finish",
            "status": "generate_dsl",
        }

    update_client_end_timestamp(client_id, str(time.time()))
    return return_message


class Response(BaseModel):
    client_id: str
    response: str


@app.post("/response")
async def handle_response(request_body: Response):
    client_id = request_body.client_id
    user_response = request_body.response
    response = followup(client_id, user_response)

    if response["type"] == "question":
        response_question = response["question"]
        response_choices = response["choices"]

        return_message = {
            "client_id": client_id,
            "question": response_question,
            "choices": response_choices,
            "type": "question",
            "status": "clarification",
        }
    elif response["type"] == "finish":
        return_message = {
            "client_id": client_id,
            "type": "finish",
            "status": "generate_dsl",
        }

    update_client_end_timestamp(client_id, str(time.time()))
    return return_message


class GenerateDSL(BaseModel):
    client_id: str


@app.post("/generate_dsl")
async def handle_generate_dsl(request_body: GenerateDSL):
    client_id = request_body.client_id

    response = dsl_synthesize(client_id)
    return_message = {"dsl": response, "status": "finish"}
    print(return_message)

    update_client_end_timestamp(client_id, str(time.time()))
    return return_message


class Program(BaseModel):
    function_name: str
    arguments: List[Union[str, int, float, None, list, dict]]
    condition: Optional[str]


class DSL(BaseModel):
    required_tables: List[str]
    program: List[Program]
    step_by_step_plan: str


class ExecuteDSLList(BaseModel):
    client_id: str
    dsl_list: DSL


@app.post("/execute_dsl_list")
async def handle_execute_dsl_list(request_body: ExecuteDSLList):
    client_id = request_body.client_id
    dsl_list = request_body.dsl_list.program
    required_tables = request_body.dsl_list.required_tables
    step_by_step_plan = request_body.dsl_list.step_by_step_plan

    output = execute_dsl_list(
        client_id, required_tables, dsl_list, step_by_step_plan, DependenciesManager
    )

    update_client_end_timestamp(client_id, str(time.time()))
    return output


@app.get("/get_dependencies/")
async def get_dependencies():
    dependency_list = DependenciesManager.get_all_nodes()
    return JSONResponse(status_code=200, content={"dependencies": dependency_list})


class EditDSL(BaseModel):
    client_id: str
    dsl: Program
    new_instruction: str


@app.post("/edit_dsl")
async def handle_edit_dsl(request_body: EditDSL):
    client_id = request_body.client_id
    dsl = request_body.dsl
    new_instruction = request_body.new_instruction

    update_client_end_timestamp(client_id, str(time.time()))
    return edit_dsl(client_id, dsl, new_instruction)
