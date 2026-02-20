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

from fastapi import APIRouter, HTTPException, Depends
from ..dependencies.permissions import require_edit_permission

from ..services.material_services import (
    add_raw_material,
    delete_raw_material,
    update_raw_material
)
from ..models.material_models import (
    AddRawMaterialRequest,
    UpdateRawMaterialRequest,
    DeleteRawMaterialRequest
)

router = APIRouter(
    prefix="/materials",
    tags=["Materials"]
)


"""
@router.get("/inventory/raw-materials/{finished_good_id}")
def read_raw_material_recipe_table(finished_good_id: str):
    try:
        data = get_raw_material_recipe(finished_good_id)
        return {"raw_materials": data}  # already a list of dicts
    except Exception:
        return {"raw_materials": []}
"""

#add a new raw material
@router.post("/add")
def add_raw_material_endpoint(data: AddRawMaterialRequest, user=Depends(require_edit_permission)):
    try:
        return add_raw_material(
            material_name=data.material_name,
            quantity=data.quantity_in_stock,
            unit_of_measure=data.unit_of_measure
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#delete a raw material
@router.delete("/delete")
def delete_raw_material_endpoint(data: DeleteRawMaterialRequest, user=Depends(require_edit_permission)):
    try:
        return delete_raw_material(material_name=data.material_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#update a raw material
@router.put("/update")
def update_raw_material_endpoint(data: UpdateRawMaterialRequest, user=Depends(require_edit_permission)):
    try:
        return update_raw_material(
            material_name=data.material_name,
            quantity=data.quantity_in_stock,
            unit_of_measure=data.unit_of_measure
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))