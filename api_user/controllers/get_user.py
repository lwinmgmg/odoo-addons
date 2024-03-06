from typing import Union
import json
import logging
from pydantic import BaseModel
from odoo import http
from odoo.http import request, Response

from ..datamodels.token import Token
from ..models.res_user_api_user import ResUserApiUser

_logger = logging.getLogger(__name__)


class GetUserResponse(BaseModel):
    login: str


class ApiUser(http.Controller):
    @classmethod
    def get_api_user(cls, token_type: str = "Bearer") -> ResUserApiUser:
        return request.env["res.users.api.user"].search(
            [("token_type", "=", token_type)]
        )

    @http.route(
        "/api_user/profile", type="http", auth="public", sitemap=False, methods=["GET"]
    )
    def api_user_profile(self, *args, **kwargs):
        auth_str: str = request.httprequest.headers.get("Authorization")
        if not auth_str:
            return Response(
                json.dumps({"message": "authorization required"}), status=401
            )
        token_type, access_token = auth_str.split(" ")
        api_user = self.get_api_user(token_type=token_type)
        if not api_user:
            return Response(
                json.dumps({"message": "No authorization config"}), status=401
            )
        try:
            claim = api_user.decode(token=access_token)
            if not api_user.reusable:
                request.env["res.users.key.expire"].validate_key(
                    key=claim.jwt_id, max_count=api_user.max_count
                )
            response = GetUserResponse(login=claim.subject.login)
            return Response(response.model_dump_json(), status=200)
        except Exception:
            _logger.exception("Falied to authorize")
            request._cr.rollback()
            return Response(
                json.dumps({"message": "authorization required"}), status=401
            )
