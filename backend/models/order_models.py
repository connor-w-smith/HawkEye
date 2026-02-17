from pydantic import BaseModel


class CreateProductionOrderRequest(BaseModel):
    finishedgoodid: str
    target_quantity: int