import requests
from odoo import models
from odoo.exceptions import ValidationError

from ..datamodels.ticket import TicketLineData
from ..models.ticket import DEFAULT_HEADER

class TicketLineUpdate(models.TransientModel):
    _inherit = "dt.ticket.line"
    _name = "dt.ticket.line.wizard"

    _description = "Ticket Lines Wizard"

    def action_update(self):
        data = TicketLineData(
            sync_id=self.sync_id,
            ticket_id=self.ticket_id.sync_id,
            number=self.number,
            state=self.state,
            user_code=self.user_code or "",
            is_special_price=self.is_special_price,
            special_price=self.special_price
        )
        url = "http://0.0.0.0:8000/graphql"
        payload = """
            mutation updateTicketLine($data: [JSON!]!){
                updateTicketLine(dataList: $data){
                    id
                }
            }
        """
        res = requests.post(url=url, json={
            "query": payload,
            "variables": {
                "data": [data.model_dump(by_alias=True)]
            }
        }, headers=DEFAULT_HEADER)
        if res.status_code != 200 or res.json().get("errors"):
            raise ValidationError("Failed to update data")
        data.ticket_id = self.ticket_id.id
        return self.env["dt.ticket.line"].search([("sync_id", "=", data.sync_id)]).write(data.model_dump())
