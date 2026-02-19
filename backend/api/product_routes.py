"""
===========================================
product_routes.py
===========================================
Purpose:
Defines all product and inventory-related API endpoints.

This file ONLY contains:
- FastAPI route definitions
- Request validation
- HTTPException handling

Business logic is handled in:
services/product_services.py

Models are defined in:
models/product_models.py
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from..dependencies.permissions import require_admin, require_edit_permission

from ..models.product_models import (
    AddFinishedGood,
    DeleteFinishedGood,
)

from ..services.product_services import (
    add_finished_good,
    delete_finished_good,
    add_inventory,
    delete_inventory,
)

from ..services.search_services import (
    search_finished_goods_fuzzy,
    search_inventory_by_id,
)

router = APIRouter(
    prefix="/products",
    tags=["Products"]
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

@router.post("/add-finished-good")
def add_finished_good_endpoint(data: AddFinishedGood,user=Depends(require_edit_permission)):
    try:
        #call function from inventory.py
        return add_finished_good(data.finished_good_name)

    except Exception as e:
        #Convert errors to HTTP responses
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/delete-finished-good")
def delete_finished_good_endpoint(data: DeleteFinishedGood,user=Depends(require_edit_permission)):
    try:
        return delete_finished_good(data.finished_good_name)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/finished-goods/{finished_good_id}")
def read_finished_good(finished_good_id: str):
    finished_good = get_finished_good_by_id(finished_good_id)
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


@router.get("/inventory/{finished_good_id}")
def read_available_inventory(finished_good_id: str):
    try:
        return get_production_inventory_by_finishedgoodid(finished_good_id)
    except Exception:
        return {"AvailableInventory": 0}