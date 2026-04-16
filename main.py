from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Optional
import json
import os

from database import get_connection, init_db

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(title="HappyRobot Loads API", version="1.0.0")
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# API key auth
# ---------------------------------------------------------------------------
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

KEYS_FILE = os.path.join(os.path.dirname(__file__), "api_keys.json")


def load_api_keys() -> list[str]:
    if not os.path.exists(KEYS_FILE):
        return []
    with open(KEYS_FILE) as f:
        return json.load(f)


def verify_api_key(key: str = Security(api_key_header)):
    if key not in load_api_keys():
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return key


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
class Load(BaseModel):
    load_id: str
    origin: str
    destination: str
    equipment_type: str
    pickup_datetime: Optional[str] = None
    delivery_datetime: Optional[str] = None
    loadboard_rate: Optional[float] = None
    notes: Optional[str] = None
    weight: Optional[float] = None
    commodity_type: Optional[str] = None
    num_of_pieces: Optional[int] = None
    miles: Optional[float] = None
    dimensions: Optional[str] = None
    call_result: Optional[str] = None
    mc_number: Optional[int] = None
    agreed_rate: Optional[float] = None
    assigned: str = "no"


class LoadUpdate(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    pickup_datetime: Optional[str] = None
    delivery_datetime: Optional[str] = None
    equipment_type: Optional[str] = None
    loadboard_rate: Optional[float] = None
    notes: Optional[str] = None
    weight: Optional[float] = None
    commodity_type: Optional[str] = None
    num_of_pieces: Optional[int] = None
    miles: Optional[float] = None
    dimensions: Optional[str] = None
    call_result: Optional[str] = None
    mc_number: Optional[int] = None
    agreed_rate: Optional[float] = None
    assigned: Optional[str] = None


class Call(BaseModel):
    call_result: str
    decline_reason: Optional[str] = None
    call_duration: float
    agreed_rate: Optional[float] = None
    original_rate: float
    caller_satisfaction: str


class CallUpdate(BaseModel):
    call_result: Optional[str] = None
    decline_reason: Optional[str] = None
    call_duration: Optional[float] = None
    agreed_rate: Optional[float] = None
    original_rate: Optional[float] = None
    caller_satisfaction: Optional[str] = None


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def row_to_dict(row) -> dict:
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "service": "HappyRobot Loads API"}


@app.get("/loads", tags=["Loads"])
def list_loads(api_key: str = Depends(verify_api_key)):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM loads").fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@app.get("/loads/{load_id}", tags=["Loads"])
def get_load(load_id: str, api_key: str = Depends(verify_api_key)):
    conn = get_connection()
    row = conn.execute("SELECT * FROM loads WHERE load_id = ?", (load_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Load not found")
    return row_to_dict(row)


@app.post("/loads", status_code=201, tags=["Loads"])
def create_load(load: Load, api_key: str = Depends(verify_api_key)):
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO loads
               (load_id, origin, destination, pickup_datetime, delivery_datetime,
                equipment_type, loadboard_rate, notes, weight, commodity_type,
                num_of_pieces, miles, dimensions, call_result, mc_number, agreed_rate, assigned)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                load.load_id, load.origin, load.destination,
                load.pickup_datetime, load.delivery_datetime,
                load.equipment_type, load.loadboard_rate, load.notes,
                load.weight, load.commodity_type, load.num_of_pieces,
                load.miles, load.dimensions, load.call_result,
                load.mc_number, load.agreed_rate, load.assigned,
            ),
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    conn.close()
    return {"message": "Load created", "load_id": load.load_id}


@app.put("/loads/{load_id}", tags=["Loads"])
def update_load(load_id: str, update: LoadUpdate, api_key: str = Depends(verify_api_key)):
    fields = {k: v for k, v in update.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    conn = get_connection()
    row = conn.execute("SELECT load_id FROM loads WHERE load_id = ?", (load_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Load not found")

    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [load_id]
    conn.execute(f"UPDATE loads SET {set_clause} WHERE load_id = ?", values)
    conn.commit()
    conn.close()
    return {"message": "Load updated", "load_id": load_id}


@app.delete("/loads/{load_id}", tags=["Loads"])
def delete_load(load_id: str, api_key: str = Depends(verify_api_key)):
    conn = get_connection()
    row = conn.execute("SELECT load_id FROM loads WHERE load_id = ?", (load_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Load not found")
    conn.execute("DELETE FROM loads WHERE load_id = ?", (load_id,))
    conn.commit()
    conn.close()
    return {"message": "Load deleted", "load_id": load_id}


# ---------------------------------------------------------------------------
# Calls endpoints
# ---------------------------------------------------------------------------
@app.get("/calls", tags=["Calls"])
def list_calls(api_key: str = Depends(verify_api_key)):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM calls").fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@app.get("/calls/{call_id}", tags=["Calls"])
def get_call(call_id: int, api_key: str = Depends(verify_api_key)):
    conn = get_connection()
    row = conn.execute("SELECT * FROM calls WHERE id = ?", (call_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Call not found")
    return row_to_dict(row)


@app.post("/calls", status_code=201, tags=["Calls"])
def create_call(call: Call, api_key: str = Depends(verify_api_key)):
    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO calls
               (call_result, decline_reason, call_duration, agreed_rate, original_rate, caller_satisfaction)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                call.call_result, call.decline_reason, call.call_duration,
                call.agreed_rate, call.original_rate, call.caller_satisfaction,
            ),
        )
        conn.commit()
        call_id = cursor.lastrowid
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    conn.close()
    return {"message": "Call created", "id": call_id}


@app.put("/calls/{call_id}", tags=["Calls"])
def update_call(call_id: int, update: CallUpdate, api_key: str = Depends(verify_api_key)):
    fields = {k: v for k, v in update.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    conn = get_connection()
    row = conn.execute("SELECT id FROM calls WHERE id = ?", (call_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Call not found")

    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [call_id]
    conn.execute(f"UPDATE calls SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()
    return {"message": "Call updated", "id": call_id}


@app.delete("/calls/{call_id}", tags=["Calls"])
def delete_call(call_id: int, api_key: str = Depends(verify_api_key)):
    conn = get_connection()
    row = conn.execute("SELECT id FROM calls WHERE id = ?", (call_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Call not found")
    conn.execute("DELETE FROM calls WHERE id = ?", (call_id,))
    conn.commit()
    conn.close()
    return {"message": "Call deleted", "id": call_id}
