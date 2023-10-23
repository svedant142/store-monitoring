from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from models.BaseModel import Base

class Store(Base):
    __tablename__ = "store_status"

    id = Column(Integer, primary_key=True, nullable=False)
    store_id = Column(Integer)
    timestamp = Column(DateTime)
    status = Column(String, nullable=False)

class BusinessHours(Base):
    __tablename__ = "menu_hours"
    id = Column(Integer, primary_key=True, nullable=False)
    store_id = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    start_time_local = Column(DateTime)
    end_time_local = Column(DateTime)

class StoreTimezone(Base):
    __tablename__ = "store_timezone"
    store_id = Column(Integer, primary_key=True, nullable=False)
    timezone_str = Column(String, nullable=False)

class Report(Base):
    __tablename__ = "report"

    report_id = Column(String, primary_key=True,nullable=False, unique=True)
    status = Column(String, nullable=False)
    path = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)