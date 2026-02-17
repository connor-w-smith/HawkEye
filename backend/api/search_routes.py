"""
===========================================
search_routes.py
===========================================
Purpose:
Defines all search-related API endpoints.

This file ONLY contains:
- FastAPI route definitions
- Request handling
- HTTPException handling

Business logic is handled in:
services/search_services.py

No Pydantic models are used for search routes.
"""

from fastapi import APIRouter, HTTPException
from backend.services import search_finished_by_id

from ..services.search_services import (
    search_finished_goods_fuzzy,
    search_finished_by_id,
    search_inventory_by_id,
    get_orders_by_finishedgoodid,
    get_raw_material_recipe,
    get_current_orders,
)

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


#finished goods search endpoint
@router.get("/finished-goods")
def finished_goods_search(search: str | None = None):
    try:
        search = (search or "").strip()

        # Always call ONE function that searches both fields
        results = search_finished_goods_fuzzy(search)

        return {
            "status": "success",
            "count": len(results),
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


"""Inventory Tables Searches"""

@router.get("/finished-goods/{finished_good_id}")
def read_finished_good(finished_good_id: str):
    finished_good = search_finished_by_id(finished_good_id)
    if not finished_good:
        raise HTTPException(status_code=404, detail="Finished good not found")

    # Convert list to dict if needed
    if isinstance(finished_good, list):
        finished_good = finished_good[0]

    # Fetch inventory
    inventory_list = search_inventory_by_id(finished_good_id)
    inventory_count = inventory_list[0]["AvailableInventory"] if inventory_list else 0

    return {
        "finished_good": {
            "FinishedGoodID": finished_good["FinishedGoodID"],
            "FinishedGoodName": finished_good["FinishedGoodName"]
        },
        "inventory": {"AvailableInventory": inventory_count}
    }


"""Production Data table searches"""

@router.get("/production-data/{finished_good_id}")
def read_order_history(finished_good_id: str):
    try:
        return get_orders_by_finishedgoodid(finished_good_id)
    except Exception:
        return []

"""Raw Material Table Searches"""

@router.get("/inventory/raw-materials/{finished_good_id}")
def read_raw_material_recipe_table(finished_good_id: str):
    try:
        data = get_raw_material_recipe(finished_good_id)
        return {"raw_materials": data}  # already a list of dicts
    except Exception:
        return {"raw_materials": []}

"""Active Production Table Searches"""

@router.get("/production-data/current-orders/{finished_good_id}")
def read_current_order_table(finished_good_id: str):
    try:
        df = get_current_orders(finished_good_id)
        return {"current_orders": df.to_dict(orient="records")}
    except Exception:
        return {"current_orders": []}

