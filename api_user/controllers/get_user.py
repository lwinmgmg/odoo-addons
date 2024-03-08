import logging
from pydantic import BaseModel
from odoo import http
from odoo.http import request

from ..models.res_user_api_user import ResUserApiUser
from .json_controller import JsonController, HttpException

_logger = logging.getLogger(__name__)

class GetUserResponse(BaseModel):
    login: str


class ApiUser(http.Controller):
    @classmethod
    def get_api_user(cls, token_type: str = "Bearer") -> ResUserApiUser:
        return request.env["res.users.api.user"].sudo().search(
            [("token_type", "=ilike", token_type)]
        )

    @http.route(
        "/api_user/profile", type="http", auth="public", sitemap=False, methods=["GET"]
    )
    @JsonController.rest_api
    def api_user_profile(self, *args, **kwargs):
        auth_str: str = request.httprequest.headers.get("Authorization")
        if not auth_str:
            raise HttpException("authorization required", status=401)
        token_type, access_token = auth_str.split(" ")
        api_user = self.get_api_user(token_type=token_type)
        if not api_user:
            raise HttpException("authorization required [No api user]", status=401)
        try:
            claim = api_user.decode(token=access_token)
            if not api_user.reusable:
                request.env["res.users.key.expire"].sudo().validate_key(
                    key=claim.jwt_id, max_count=api_user.max_count
                )
            response = GetUserResponse(login=claim.subject.login)
            return response.model_dump()
        except Exception as err:
            _logger.exception("Falied to authorize")
            request._cr.rollback()
            raise HttpException("authorization required", status=401) from err
