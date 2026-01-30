from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import psycopg2.extras
import uuid

from inventory import add_inventory
from db import get_connection

###use uvicorn to run
#uvicorn main:app --reload

###code to open psql for database
#psql -h 98.92.53.251 -U postgres -d postgres

#start fast api
app = FastAPI(title="HawkEye Backend")

#request validation
class ManualEntry(BaseModel):
    finished_good_id: uuid.UUID
    quantity: int

@app.get("/finishedgoods")
def get_finished_goods():
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("""
            SELECT finishedgoodid, finishedgoodname
            FROM tblfinishedgoods
            ORDER BY finishedgoodname;
        """)

        results = cur.fetchall()

        cur.close()
        conn.close()

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#http endpoint
@app.post("/inventory/manual")
def manual_inventory(entry: ManualEntry):
    #positive validation
    if entry.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    #inventory addition
    try:
        add_inventory(entry.finished_good_id, entry.quantity)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Database error")

    return {"status": "inventory updated"}


