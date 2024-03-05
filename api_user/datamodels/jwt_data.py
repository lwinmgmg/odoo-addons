from typing import Any, Dict, Optional
from pydantic import BaseModel

class JwtData(BaseModel):
    login: str
    data: Optional[Dict[str, Any]] = None
