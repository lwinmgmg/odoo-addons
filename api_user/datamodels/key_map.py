from pydantic import BaseModel

class KeyMap(BaseModel):
    key: str
    expire_time: int
    count: int
