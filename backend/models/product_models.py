from pydantic import BaseModel

class FinishedGoodNameRequest(BaseModel):
    finished_good_name: str

class AddFinishedGood(BaseModel):
    finished_good_name: str

class DeleteFinishedGood(BaseModel):
    finished_good_name: str

class UpdateFinishedGood(BaseModel):
    old_finished_good_name: str
    new_finished_good_name: str