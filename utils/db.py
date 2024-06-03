import sqlite3
import json

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


def upload_sheet(client_id, sheet_id, data):
    data = json.dumps(data)
    cur.execute(
        "INSERT INTO sheets (client_id, sheet_id, version, data) VALUES (?, ?, ?, ?)",
        (client_id, sheet_id, 0, data),
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


def create_history(client_id):
    cur.execute(
        "INSERT INTO histories (client_id, history) VALUES (?, ?)", (client_id, "[]")
    )
    con.commit()


def get_history(client_id):
    cur.execute("SELECT history FROM histories WHERE client_id = ?", (client_id,))
    history = json.loads(cur.fetchone()[0])
    return history


def update_history(client_id, message):
    history = get_history(client_id)
    history.append(message)
    history = json.dumps(history)
    cur.execute(
        "UPDATE histories SET history = ? WHERE client_id = ?", (history, client_id)
    )
    con.commit()


def clear_history(client_id):
    cur.execute(
        "UPDATE histories SET history = ? WHERE client_id = ?", ("[]", client_id)
    )
    con.commit()
