from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uuid
import psycopg2
import psycopg2.extras

from db import get_connection
#from inventory import add_inventory

# Import routers ONLY from api package
from .api import (
    auth_router,
    search_router,
    order_router,
    user_router,
    product_router,
    material_router
)

app = FastAPI(title="HawkEye Backend")

# Include all routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(search_router)
app.include_router(order_router)
app.include_router(user_router)
app.include_router(product_router)
app.include_router(material_router)

# =============================
# Request validation model
# =============================
class ManualEntry(BaseModel):
    finished_good_id: uuid.UUID
    quantity: int

# =============================
# Templates & Static
# =============================
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/search")
def search_page(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

# =============================
# Finished Goods Endpoint
# =============================
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

# =============================
# Manual Inventory Endpoint
# =============================
@app.post("/inventory/manual")
def manual_inventory(entry: ManualEntry):
    if entry.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    try:
        add_inventory(entry.finished_good_id, entry.quantity)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Database error")

    return {"status": "inventory updated"}

