from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class OperatorBase(BaseModel):
    name: str
    is_active: bool = True
    load_limit: int = 10

class OperatorCreate(OperatorBase):
    pass

class Operator(OperatorBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SourceBase(BaseModel):
    name: str

class SourceCreate(SourceBase):
    pass

class Source(SourceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class AllocationSet(BaseModel):
    operator_id: int
    weight: int

class InteractionCreate(BaseModel):
    lead_identifier: str
    source_id: int
    message: Optional[str] = None

class Interaction(BaseModel):
    id: int
    lead_id: int
    source_id: int
    operator_id: Optional[int]
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Lead(BaseModel):
    id: int
    identifier: str
    model_config = ConfigDict(from_attributes=True)
