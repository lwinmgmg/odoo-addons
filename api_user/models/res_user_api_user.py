from typing import Optional
from uuid import uuid4
from datetime import datetime, timedelta
import jwt
from odoo import fields, models

from ..datamodels.jwt_data import JwtData
from ..datamodels.registered_claim import RegisteredClaim


JWT_ALGORITHM = "HS256"


class ResUserApiUser(models.Model):
    _name = "res.users.api.user"

    _description = "JwT support for api users"

    issuer: str = fields.Char()
    audience: str = fields.Char()
    secret: str = fields.Char()
    algorithm: str = fields.Char()
    token_type: str = fields.Char(index=True)
    duration: int = fields.Integer()
    reusable: bool = fields.Boolean()
    max_count: int = fields.Integer(default=1)
    active: bool = fields.Boolean(default=True, index=True)

    _sql_constraints = [
        (
            "token_type_unique_odoo",
            "unique (token_type)",
            "Can't be used old token_type",
        )
    ]

    def encode(self, login: Optional[str] = "") -> str:
        now_time = datetime.utcnow()
        exp_time = now_time + timedelta(seconds=self.duration)
        jwt_id = uuid4().hex
        self.env["res.users.key.expire"].add_key(key=jwt_id, expire_time=exp_time, count=self.max_count)
        return jwt.encode(
            RegisteredClaim(
                exp=int(exp_time.timestamp()),
                nbf=int(now_time.timestamp()),
                iss=self.issuer,
                aud=self.audience,
                iat=int(now_time.timestamp()),
                jti=jwt_id,
                sub=JwtData(login=login if login else self.env.user.login),
            ).model_dump(by_alias=True),
            self.secret,
            algorithm=self.algorithm,
        )

    def decode(self, token: str, verify: bool = True) -> RegisteredClaim:
        data = jwt.decode(
            token,
            key=self.secret,
            algorithms=[self.algorithm],
            verify=verify,
            audience=self.audience,
            issuer=self.issuer,
        )
        return RegisteredClaim.model_validate(data)
