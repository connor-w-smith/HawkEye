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

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict

from ..services import get_upcoming_orders_by_sensor, get_completed_orders_by_sensor, last_five_orders_production_rate, \
    current_order_production_rate
from ..services.search_services import (
    search_finished_goods_fuzzy,
    search_finished_by_id,
    search_inventory_by_id,
    get_orders_by_finishedgoodid,
    get_currently_packaging,
    get_finished_goods_with_quantities,
    get_active_order_for_finishedgood,
    get_sensor_production_amounts,
    get_upcoming_orders,
    get_completed_orders,
    get_completed_orders
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


#finished goods with production quantities endpoint
@router.get("/finished-goods-with-quantities")
def finished_goods_with_quantities():
    try:
        results = get_finished_goods_with_quantities()

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
def read_order_history(finished_good_id: str, days: int = 7):
    try:
        return get_orders_by_finishedgoodid(finished_good_id, days)
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
        data = get_active_order_for_finishedgood(finished_good_id)
        return {"current_orders": data}
    except Exception:
        return {"current_orders": []}


@router.get("/active-orders", response_model=List[Dict])
async def read_active_orders():
    try:
        data = get_currently_packaging()

        if not data:
            return[]

        return data

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sensor-stats", response_model=List[Dict])
async def read_sensor_stats():
    try:
        production = get_sensor_production_amounts()
        if production is None:
            return []

        return production

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/upcoming-orders", response_model=List[Dict])
async def read_upcoming_orders():
    try:
        data = get_upcoming_orders()

        if not data:
            return []

        return data

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/completed-orders", response_model=List[Dict])
def read_completed_orders(timeframe: int = Query(default=7, ge=1)):
    try:
        return get_completed_orders(timeframe) or []
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/order-history")
def order_history(days: int = 7):
    try:
        results = get_completed_orders(days)

        return {
            "status": "success",
            "count": len(results),
            "orders": results
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/upcoming-orders-sensor", response_model=List[Dict])
async def read_upcoming_orders_by_sensor(sensorid: str):
    try:
        data = get_upcoming_orders_by_sensor(sensorid)

        if not data:
            return []

        return data

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/order-history-sensor", response_model=List[Dict])
def order_history(sensorid: str):
    try:
        results = get_completed_orders_by_sensor(sensorid)

        if not results:
            return []

        return results

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/current-production-rate", response_model=List[Dict])
def current_production_rate(sensorid: str):
    try:
        results = current_order_production_rate(sensorid)

        if not results:
            return []

        return results

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/previous-order-production-rate", response_model=List[Dict])
def previous_order_production_rate(sensorid: str):
    try:
        results = last_five_orders_production_rate(sensorid)

        if not results:
            return []

        return results

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

