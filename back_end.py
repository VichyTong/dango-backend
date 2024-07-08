from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from io import StringIO
import os
import uuid
import re
import json
import aiofiles
import pandas as pd


from utils.analyze import multi_analyze, followup
from utils.synthesize import dsl_synthesize
from utils.llm import (
    append_message,
    generate_chat_completion,
)
from utils.db import (
    create_client,
    upload_sheet,
    get_sheet,
    delete_sheet,
    is_sheet_exists,
    get_all_sheets,
    get_same_sheet_version,
    find_next_version,
    get_history,
)
from utils.execute import execute_dsl
from utils.dependency import DependenciesManager
from utils.log import log_messages, log_text

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

# Initialize dependencies manager
DependenciesManager = DependenciesManager()


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
            "is_index_table": sheet_info["is_index_table"],
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
    else:
        return_message = {
            "client_id": client_id,
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

    return return_message


class GenerateDSL(BaseModel):
    client_id: str


@app.post("/generate_dsl")
async def handle_generate_dsl(request_body: GenerateDSL):
    client_id = request_body.client_id

    response = dsl_synthesize(client_id)
    return_message = {"dsl": response, "status": "finish"}
    return return_message


class DSL(BaseModel):
    function_name: str
    arguments: List[Union[str, int]]


class ExecuteDSLList(BaseModel):
    client_id: str
    dsl_list: List[DSL]


@app.post("/execute_dsl_list")
async def handle_execute_dsl_list(request_body: ExecuteDSLList):
    client_id = request_body.client_id
    dsl_list = request_body.dsl_list

    # table-level operations
    table_function_list = [
        "delete_table",
        "create_table",
    ]
    # table_name in arguments[0]
    type_a_function_list = [
        "insert",
        "drop",
        "assign",
        "concatenate",
        "split",
        "transpose",
        "aggregate",
        "test",
    ]
    # table_name_a in arguments[0], table_name_b in arguments[2]
    type_b_function_list = [
        "move",
        "copy",
        "swap",
    ]
    # table_name_a in arguments[0], table_name_b in arguments[1]
    type_c_function_list = [
        "merge",
    ]

    def split_sheet_name(sheet_name):
        # Regular expression to find "v{int}" suffix
        match = re.search(r"_v(\d+)\.csv$", sheet_name)
        if match:
            # Extract base name and version number
            base_name = sheet_name[: match.start()] + ".csv"
            version = int(match.group(1))
        else:
            # No version number present
            base_name = sheet_name
            version = 0

        return base_name, version

    def get_sheet_info(sheet_name):
        sheet_id, version = split_sheet_name(sheet_name)
        sheet_data = get_sheet(client_id, sheet_id, version)
        sheet = pd.DataFrame(sheet_data)
        flag = False
        if "Unnamed: 0" in sheet.columns:
            flag = True
            sheet = pd.DataFrame(sheet_data, index_col=0)
        return sheet

    tmp_sheet_data_map = {}
    tmp_sheet_version_map = {}

    def load_sheet(sheet_name):
        sheet_id, sheet_version = split_sheet_name(sheet_name)
        if sheet_id not in tmp_sheet_data_map:
            tmp_sheet_data_map[sheet_id] = get_sheet_info(sheet_name)
            print(sheet_id)
            print(sheet_version)
            tmp_sheet_version_map[sheet_id] = sheet_version
        else:
            if tmp_sheet_version_map[sheet_id] != sheet_version:
                log_text(
                    client_id,
                    f">>> Execute_DSL\nError: {sheet_id} version {tmp_sheet_version_map[sheet_id]} and {sheet_version} mismatch.",
                )
                return None

    for dsl in dsl_list:
        function = dsl.function_name
        arguments = dsl.arguments
        DependenciesManager.update_dependency(function, arguments)
        if function in table_function_list:
            sheet_id = arguments[0]
            if function == "create_table":
                # create a dataframe have row_number and column_number
                row_number = arguments[1]
                column_number = arguments[2]
                data = pd.DataFrame(
                    index=range(row_number), columns=range(column_number)
                )
                upload_sheet(client_id, sheet_id, 0, data.to_dict(orient="records"))
                tmp_sheet_data_map[sheet_id] = data
                tmp_sheet_version_map = 0
            elif function == "delete_table":
                version = find_next_version(client_id, sheet_id) - 1
                if version < 0:
                    print("Error: Invalid Table")
                delete_sheet(
                    client_id,
                    sheet_id=sheet_id,
                    version=version,
                )
                print(sheet_id, version)
                print(get_all_sheets(client_id))
        elif function in type_a_function_list:
            load_sheet(arguments[0])
            sheet_id, _ = split_sheet_name(arguments[0])
            sheet = tmp_sheet_data_map[sheet_id]
            new_sheet = execute_dsl(sheet, function, arguments[1:])
            new_data = new_sheet.fillna("").to_json(orient="records")
            if function == "test":
                tmp_sheet_data_map["Test_Result.csv"] = new_sheet
                upload_sheet(
                    client_id, "Test_Result.csv", 0, new_sheet.to_dict(orient="records")
                )
            else:
                tmp_sheet_data_map[sheet_id] = new_sheet
        elif function in type_b_function_list:
            load_sheet(arguments[0])
            load_sheet(arguments[2])
            sheet_id, _ = split_sheet_name(arguments[0])
            target_sheet_id, _ = split_sheet_name(arguments[2])
            sheet = tmp_sheet_data_map[sheet_id]
            target_sheet = tmp_sheet_data_map[target_sheet_id]
            new_sheet, new_target_sheet = execute_dsl(
                sheet,
                function,
                [arguments[1]] + arguments[3:],
                target_sheet=target_sheet,
            )
            new_data = new_sheet.fillna("").to_json(orient="records")
            new_target_data = new_target_sheet.fillna("").to_json(orient="records")
            tmp_sheet_data_map[sheet_id] = new_sheet
            tmp_sheet_data_map[target_sheet_id] = new_target_sheet
        elif function in type_c_function_list:
            load_sheet(arguments[0])
            load_sheet(arguments[1])
            sheet_id, _ = split_sheet_name(arguments[0])
            target_sheet_id, _ = split_sheet_name(arguments[1])
            sheet = tmp_sheet_data_map[sheet_id]
            target_sheet = tmp_sheet_data_map[target_sheet_id]
            new_sheet, new_target_sheet = execute_dsl(
                sheet,
                function,
                arguments[2:],
                target_sheet=target_sheet,
            )
            new_data = new_sheet.fillna("").to_json(orient="records")
            new_target_data = new_target_sheet.fillna("").to_json(orient="records")
            tmp_sheet_data_map[sheet_id] = new_sheet
            tmp_sheet_data_map[target_sheet_id] = new_target_sheet
        else:
            return "Error: Invalid function"

    output = []
    for sheet_id, sheet in tmp_sheet_data_map.items():
        sheet_data = sheet.fillna("").to_dict(orient="records")
        same_sheet_version = get_same_sheet_version(client_id, sheet_id, sheet_data)
        if same_sheet_version:
            output.append(
                {
                    "sheet_id": sheet_id,
                    "version": same_sheet_version,
                    "data": sheet_data,
                }
            )
            continue
        sheet_version = find_next_version(client_id, sheet_id)
        upload_sheet(client_id, sheet_id, sheet_version, sheet_data)
        output.append(
            {"sheet_id": sheet_id, "version": sheet_version, "data": sheet_data}
        )
    return output


@app.get("/get_dependencies/")
async def get_dependencies():
    dependency_list = DependenciesManager.get_all_nodes()
    return JSONResponse(status_code=200, content={"dependencies": dependency_list})
