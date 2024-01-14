import json
from google_auth_oauthlib.flow import Flow
from odoo import http
from odoo.http import request

class GdriveLogin(http.Controller):
    @http.route('/gdrive/login', type='http', auth="user", sitemap=False, methods=["GET"])
    def gdrive_login(self, *args, **kwargs):
        state = kwargs.get('state')
        params_str = request.env['ir.config_parameter'].get_param(state) or "{}"
        params = json.loads(params_str)
        record = request.env["gdrive.settings"].browse([params.get('id')])
        redirect_uri = f"{request.env['ir.config_parameter'].get_param('web.base.url')}/gdrive/login"
        flow = Flow.from_client_config(json.loads(record.credential_json), scopes=record.scopes.split(","), state=state)
        flow.redirect_uri = redirect_uri
        flow.fetch_token(authorization_response=request.httprequest.url)
        record.update({
            'token_json': flow.credentials.to_json()
        })
        return request.redirect(params.get('current_uri') or "/")
