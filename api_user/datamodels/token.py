from pydantic import BaseModel, Field

class Token(BaseModel):
    access_token: str = Field(alias="atn")
    token_type: str = Field(alias="ttp")
