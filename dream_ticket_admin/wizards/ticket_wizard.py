import requests
from odoo import models
from odoo.exceptions import ValidationError

from ..datamodels.ticket import TicketData
from ..models.ticket import get_dt_header

class TicketUpdate(models.TransientModel):
    _inherit = "dt.ticket"
    _name = "dt.ticket.wizard"

    _description = "Ticket Wizard"

    def action_create(self):
        url = "http://0.0.0.0:8000/graphql"
        payload = """
            mutation addTicket($data: JSON!){
                addTicket(data: $data){
                    id
                }
            }
        """
        data = TicketData.model_validate(self, from_attributes=True).model_dump()
        data.pop("sync_id")
        data["sync_user"] = self.env.user.login
        res = requests.post(url=url, json={
            "query": payload,
            "variables": {
                "data": data
            }
        }, headers=get_dt_header(self))
        if res.status_code != 200 or res.json().get("errors"):
            raise ValidationError(f"Unable to create ticket : {res.json()}")
        return self.env["dt.ticket"].action_refresh_ticket()

    def action_update(self):
        data = TicketData.model_validate(self, from_attributes=True)
        url = "http://0.0.0.0:8000/graphql"
        payload = """
            mutation updateTicket($data: [JSON!]!){
                updateTicket(dataList: $data){
                    id
                }
            }
        """
        res = requests.post(url=url, json={
            "query": payload,
            "variables": {
                "data": [data.model_dump(by_alias=True)]
            }
        }, headers=get_dt_header(self))
        if res.status_code != 200 or res.json().get("errors"):
            raise ValidationError("Failed to update data")
        return self.env["dt.ticket"].search([("sync_id", "=", data.sync_id)]).write(data.model_dump())
