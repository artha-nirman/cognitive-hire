from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class PermissionResponse(PermissionBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class PermissionListResponse(BaseModel):
    items: List[PermissionResponse]
    total: int
