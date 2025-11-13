from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean

Base=declarative_base()

@dataclass
class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    done = Column(Boolean, default=False)
