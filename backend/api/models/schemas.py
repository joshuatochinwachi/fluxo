from pydantic import BaseModel, Field, field_validator 
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PortfolioInput(BaseModel):
    wallet_address: str = Field(..., min_length=42, max_length=42)
    network: str = Field(default="mantle")
    
    @field_validator('wallet_address')
    def validate_address(cls, v):
        if not v.startswith('0x'):
            raise ValueError('Invalid wallet address')
        return v.lower()

class RiskScore(BaseModel):
    score: float = Field(..., ge=0, le=100)
    level: RiskLevel
    factors: Dict[str, float] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
