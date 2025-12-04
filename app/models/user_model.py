from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """User data model for MongoDB."""
    
    email: EmailStr
    password_hash: str
    fullname: Optional[str] = None
    avatar: Optional[str] = None
    dob: Optional[datetime] = None
    is_verified: bool = False
    verification_code: Optional[str] = None
    verification_code_expires_at: Optional[datetime] = None
    password_reset_token: Optional[str] = None
    password_reset_token_expires_at: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password_hash": "hashed_password",
                "fullname": "John Doe",
                "avatar": "https://example.com/avatar.jpg",
                "dob": "1990-01-01T00:00:00",
                "is_verified": False,
                "verification_code": "123456",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
