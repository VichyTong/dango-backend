import sqlite3
import json
import uuid

from utils.format_text import convert_history_to_text, convert_history_to_dumped_text

con = sqlite3.connect("clean.db")

cur = con.cursor()

cur.execute(
    """
CREATE TABLE IF NOT EXISTS histories (
    client_id TEXT PRIMARY KEY,
    history TEXT
)
"""
)

cur.execute(
    """
CREATE TABLE IF NOT EXISTS sheets (
    client_id TEXT,
    sheet_id TEXT,
    version INTEGER,
    data TEXT,
    PRIMARY KEY (client_id, sheet_id, version)
)
"""
)


def upload_sheet(client_id, sheet_id, version, data):
    data = json.dumps(data)
    cur.execute(
        "INSERT INTO sheets (client_id, sheet_id, version, data) VALUES (?, ?, ?, ?)",
        (client_id, sheet_id, version, data),
    )
    con.commit()


def get_sheet(client_id, sheet_id, version):
    cur.execute(
        "SELECT data FROM sheets WHERE client_id = ? AND sheet_id = ? AND version = ?",
        (client_id, sheet_id, version),
    )
    data = json.loads(cur.fetchone()[0])
    return data


def delete_sheet(client_id, sheet_id, version):

    cur.execute(
        "DELETE FROM sheets WHERE client_id = ? AND sheet_id = ? AND version = ?",
        (client_id, sheet_id, version),
    )
    con.commit()


def is_sheet_exists(client_id, sheet_id, version):
    cur.execute(
        "SELECT * FROM sheets WHERE client_id = ? AND sheet_id = ? AND version = ?",
        (client_id, sheet_id, version),
    )
    return cur.fetchone() is not None


def get_all_sheets(client_id):
    cur.execute(
        "SELECT sheet_id, version FROM sheets WHERE client_id = ?", (client_id,)
    )
    sheets = cur.fetchall()
    return sheets


def get_same_sheet_version(client_id, sheet_id, data):
    cur.execute(
        "SELECT version, data FROM sheets WHERE client_id = ? AND sheet_id = ?",
        (client_id, sheet_id),
    )
    versions = cur.fetchall()
    for version, sheet_data in versions:
        if json.loads(sheet_data) == data:
            return version
    return None


def find_next_version(client_id, sheet_id):
    cur.execute(
        "SELECT version FROM sheets WHERE client_id = ? AND sheet_id = ?",
        (client_id, sheet_id),
    )
    versions = cur.fetchall()
    if len(versions) == 0:
        return 0
    else:
        return max([version[0] for version in versions]) + 1


def create_history(client_id):
    cur.execute(
        "INSERT INTO histories (client_id, history) VALUES (?, ?)", (client_id, "{}")
    )
    con.commit()


def get_history(client_id):
    cur.execute("SELECT history FROM histories WHERE client_id = ?", (client_id,))
    history = json.loads(cur.fetchone()[0])
    return history


def update_history(client_id, history):
    history = json.dumps(history)
    cur.execute(
        "UPDATE histories SET history = ? WHERE client_id = ?", (history, client_id)
    )
    con.commit()


def create_client():
    client_id = str(uuid.uuid4())
    create_history(client_id)
    return client_id


"""
Organization of "history"
{
    "infomation": <string>,
    "question_answer_list": [
        {
            "summary": <string>,
            "question": <string>,
            "choices": [<string>, <string>, ...],
            "answer": <string>,
        },
        ...
    ]
}
"""
