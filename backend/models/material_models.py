from pydantic import BaseModel
from typing import Optional

#request model for adding a new raw material
class AddRawMaterialRequest(BaseModel):
    material_name: str
    quantity_in_stock: float
    unit_of_measure: str


#request model for updating an existing raw material
class UpdateRawMaterialRequest(BaseModel):
    material_name: str
    quantity_in_stock: Optional[float] = None  #only update if provided
    unit_of_measure: Optional[str] = None      #only update if provided


#request model for deleting a raw material
class DeleteRawMaterialRequest(BaseModel):
    material_name: str
