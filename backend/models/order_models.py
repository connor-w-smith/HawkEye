from pydantic import BaseModel
from typing import Optional


class CreateProductionOrderRequest(BaseModel):
    finishedgoodid: str
    target_quantity: int
    sensor_id: Optional[str] = None  # Optional sensor ID to link this order to a specific sensor

class DeleteProductionOrderRequest(BaseModel):
    orderid: str

class EditProductionOrder(BaseModel):
    orderid: str
    finishedgoodid: str
    target_quantity: int
    sensor_id: str