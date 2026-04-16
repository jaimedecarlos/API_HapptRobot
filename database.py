import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "loads.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loads (
            load_id          TEXT PRIMARY KEY,
            origin           TEXT,
            destination      TEXT,
            pickup_datetime  TEXT,
            delivery_datetime TEXT,
            equipment_type   TEXT,
            loadboard_rate   REAL,
            notes            TEXT,
            weight           REAL,
            commodity_type   TEXT,
            num_of_pieces    INTEGER,
            miles            REAL,
            dimensions       TEXT,
            call_result      TEXT,
            mc_number        INTEGER,
            agreed_rate      REAL,
            assigned         TEXT NOT NULL DEFAULT 'no'
        )
    """)
    # Migrate existing databases that predate these columns
    existing = {row[1] for row in cursor.execute("PRAGMA table_info(loads)")}
    for col, definition in [
        ("call_result", "TEXT"),
        ("mc_number", "INTEGER"),
        ("agreed_rate", "REAL"),
        ("assigned", "TEXT NOT NULL DEFAULT 'no'"),
    ]:
        if col not in existing:
            cursor.execute(f"ALTER TABLE loads ADD COLUMN {col} {definition}")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            call_result          TEXT NOT NULL,
            decline_reason       TEXT,
            call_duration        REAL NOT NULL,
            agreed_rate          REAL NOT NULL,
            original_rate        REAL NOT NULL,
            caller_satisfaction  TEXT NOT NULL
        )
    """)

    # Migrate existing calls tables that predate caller_satisfaction
    existing_calls = {row[1] for row in cursor.execute("PRAGMA table_info(calls)")}
    if "caller_satisfaction" not in existing_calls:
        cursor.execute("ALTER TABLE calls ADD COLUMN caller_satisfaction TEXT NOT NULL DEFAULT ''")

    conn.commit()
    conn.close()
