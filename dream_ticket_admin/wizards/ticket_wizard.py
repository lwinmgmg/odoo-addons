import requests
from odoo import models
from odoo.exceptions import ValidationError

class TicketUpdate(models.TransientModel):
    _inherit = "dt.ticket"
    _name = "dt.ticket.wizard"

    _description = "Ticket Wizard"

    def action_create(self):
        url = "http://0.0.0.0:8000/graphql"
        headers = {
            "content-type": "application/json"
        }
        payload = """
            mutation{
                addTicket(data: {
                    name: "%s",
                    description:"%s",
                    start_num: %s,
                    end_num: %s,
                    available_count: %s,
                    state: %s,
                    sync_user: "%s"
                }){
                    id
                }
            }
        """%(self.name, self.description, self.start_num, self.end_num, self.end_num - self.start_num + 1, self.state, self.env.user.login)
        res = requests.post(url=url, json={
            "query": payload
        }, headers=headers)
        if res.status_code != 200 or res.json().get("error"):
            raise ValidationError(f"Unable to create ticket : {res.json()}")
        return self.env["dt.ticket"].action_refresh_ticket()
