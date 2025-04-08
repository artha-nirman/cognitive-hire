from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class RoleResponse(RoleBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class RoleListResponse(BaseModel):
    items: List[RoleResponse]
    total: int
