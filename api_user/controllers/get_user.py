import json
from pydantic import BaseModel
from odoo import http
from odoo.http import request, Response

from ..datamodels.token import Token
from ..models.res_user_api_user import ResUserApiUser

class GetUserResponse(BaseModel):
    login: str

class ApiUser(http.Controller):
    @classmethod
    def get_api_user(cls, token_type: str = "Bearer") -> ResUserApiUser:
        return request.env["res.users.api.user"].search([("token_type", "=", token_type)])

    @http.route('/api_user/profile', type='http', auth="public", sitemap=False, methods=["GET"])
    def gdrive_login(self, *args, **kwargs):
        auth_str: str = request.httprequest.headers.get("Authorization")
        if not auth_str:
            return Response(json.dumps({"message": "authorization required"}), status=401)
        token_type, access_token = auth_str.split(" ")
        token = Token(
            atn=access_token,
            ttp=token_type
        )
        
        api_user = self.get_api_user(token_type=token_type)
        if not api_user:
            return Response(json.dumps({"message": "No authorization config"}), status=401)
        try:
            if not api_user.reusable:
                ...
            claim = api_user.decode(token=access_token)
            response = GetUserResponse(login=claim.subject.login)
            return Response(response.model_dump_json(), status=200)
        except Exception:
            request._cr.rollback()
            return Response(json.dumps({"message": "authorization required"}), status=401)
