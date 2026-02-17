"""
===========================================
material_routes.py
===========================================
Purpose:
Defines all raw-material-related API endpoints.

This file ONLY contains:
- FastAPI route definitions
- Request validation
- HTTPException handling

Business logic is handled in:
services/material_services.py

Models are defined in:
models/material_models.py
"""

from fastapi import APIRouter, HTTPException
from ..services.material_services import get_raw_material_recipe
from ..models.material_models import RawMaterialRequest

router = APIRouter(
    prefix="/materials",
    tags=["Materials"]
)



@router.get("/inventory/raw-materials/{finished_good_id}")
def read_raw_material_recipe_table(finished_good_id: str):
    try:
        data = get_raw_material_recipe(finished_good_id)
        return {"raw_materials": data}  # already a list of dicts
    except Exception:
        return {"raw_materials": []}