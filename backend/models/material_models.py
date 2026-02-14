from pydantic import BaseModel

class RawMaterialRequest(BaseModel):
    finished_good_id: str
