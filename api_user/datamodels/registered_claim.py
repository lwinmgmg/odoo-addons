from pydantic import BaseModel, Field

from .jwt_data import JwtData

class RegisteredClaim(BaseModel):
    expire: int = Field(alias="exp")
    not_before: int = Field(alias="nbf")
    issuer: str = Field(alias="iss")
    audience: str = Field(alias="aud")
    issued_at: int = Field(alias="iat")
    jwt_id: str = Field(alias="jti")
    subject: JwtData = Field(alias="sub")
