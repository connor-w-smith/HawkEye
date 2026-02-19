"""
===========================================
order_routes.py
===========================================
Purpose:
Defines all production order-related API endpoints.

This file ONLY contains:
- FastAPI route definitions
- Request validation
- HTTPException handling

Business logic is handled in:
services/order_services.py

Models are defined in:
models/order_models.py
"""

from fastapi import APIRouter, HTTPException

from ..services import create_new_order

'''
not implemented yet ;p
from ..services.order_services import (
    get_orders_by_finishedgoodid,
    get_current_orders,
    create_production_order as create_production_order_service
)
'''
from ..models.order_models import CreateProductionOrderRequest

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.get("/production-data/{finished_good_id}")
def read_order_history(finished_good_id: str):
    try:
        return get_orders_by_finishedgoodid(finished_good_id)
    except Exception:
        return []


@router.get("/production-data/current-orders/{finished_good_id}")
def read_current_order_table(finished_good_id: str):
    try:
        df = get_current_orders(finished_good_id)
        return {"current_orders": df.to_dict(orient="records")}
    except Exception:
        return {"current_orders": []}


#TODO: Break this apart and add DB portion to order_services file
# Create a new production order
@router.post("/create")
async def create_production_order(finishedgoodid: str, target_quantity: int):

    try:
        result = create_new_order(finishedgoodid, target_quantity)

        return result

    except Exception as e:
        print(f"Error creating production order: {e}")
        raise Exception(f"Failed to create production order: {str(e)}")