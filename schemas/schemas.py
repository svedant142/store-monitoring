from pydantic import BaseModel
from datetime import datetime

class Store(BaseModel):
    id: int
    timestamp: datetime
    status: str

class BusinessHours(BaseModel):
    store_id: int
    day_of_week: int
    start_time_local: datetime.time
    end_time_local: datetime.time

class StoreTimezone(BaseModel):
    store_id: int
    timezone_str: str

class Report(BaseModel):
    report_id: str
    status: str
    path: str
    created_at: datetime
    completed_at: datetime

    class Config:
        orm_mode = True