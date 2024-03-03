from typing import List, Tuple
from enum import Enum
import requests
from odoo import fields, models


class TicketState(Enum):
    DRAFT = "draft"
    POSTED = "posted"
    DONE = "done"

    @classmethod
    def name_value(cls) -> List[Tuple[str, str]]:
        return [(tmp.name, tmp.value) for tmp in cls]


class Ticket(models.Model):
    _name = "dt.ticket"

    _description = "Tickets"

    name = fields.Char()
    state = fields.Selection(TicketState.name_value())
    description = fields.Text()
    start_num = fields.Integer()
    end_num = fields.Integer()
    win_num = fields.Integer()
    available_count = fields.Integer()
    reserved_count = fields.Integer()
    sold_count = fields.Integer()
    line_ids = fields.One2many(comodel_name="dt.ticket.line", inverse_name="ticket_id")
    sync_id = fields.Integer(index=True)

    def action_update_ticket(self): ...

    def action_refresh_ticket(self):
        self.search([]).unlink()
        res = requests.post(
            "http://0.0.0.0:8000/graphql",
            data="{\"query\":\"query{\\r\\n    ticketQuery(query:{\\r\\n        domain: [[\\\"sync_user\\\", \\\"=\\\", \\\"%s\\\"]],\\r\\n        order: {}\\r\\n    }){\\r\\n        id,\\r\\n        name,\\r\\n        state,\\r\\n        description,\\r\\n        startNum,\\r\\n        endNum,\\r\\n        winNum,\\r\\n        availableCount,\\r\\n        reservedCount,\\r\\n        soldCount\\r\\n    }\\r\\n}\\r\\n\",\"variables\":{}}"%(self.env.user.login,),
            headers={"content-type": "application/json"},
        )
        data = res.json()
        tickets = data.get("data").get("ticketQuery")
        for ticket in tickets:
            self.create(
                {
                    "sync_id": ticket.get("id"),
                    "name": ticket.get("name"),
                    "state": ticket.get("state"),
                    "description": ticket.get("description"),
                    "start_num": ticket.get("startNum"),
                    "end_num": ticket.get("endNum"),
                    "win_num": ticket.get("winNum"),
                    "available_count": ticket.get("availableCount"),
                    "reserved_count": ticket.get("reservedCount"),
                    "sold_count": ticket.get("soldCount")
                }
            )
        return self.env.ref("dream_ticket_admin.action_dt_ticket").read()[0]

    def action_update_ticket_line(self):
        self.line_ids.unlink()
        res = requests.post(
            "http://0.0.0.0:8000/graphql",
            data="{\"query\":\"query{\\r\\n    ticket(id: %s){\\r\\n        lines{\\r\\n            id,\\r\\n            number,\\r\\n            userCode,\\r\\n            state,\\r\\n            isSpecialPrice,\\r\\n            specialPrice\\r\\n        }\\r\\n    }\\r\\n}\",\"variables\":{}}"%(self.sync_id,),
            headers={"content-type": "application/json"},
        )
        data = res.json()
        tickets = data.get("data").get("ticket")
        return self.env["dt.ticket.line"].create([{
            "ticket_id": self.id,
            "sync_id": line.get("id"),
            "number": line.get("number"),
            "state": line.get("state"),
            "user_code": line.get("userCode"),
            "is_special_price": line.get("isSpecialPrice"),
            "special_price": line.get("specialPrice"),
        } for line in tickets.get("lines")])


class TicketUpdate(models.TransientModel):
    _inherit = "dt.ticket"
    _name = "dt.ticket.wizard"

    _description = "Ticket Wizard"


class TicketLineState(Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"

    @classmethod
    def name_value(cls) -> List[Tuple[str, str]]:
        return [(tmp.name, tmp.value) for tmp in cls]


class TicketLine(models.Model):
    _name = "dt.ticket.line"

    _description = "Ticket Lines"

    number = fields.Integer()
    ticket_id = fields.Many2one(comodel_name="dt.ticket", ondelete="cascade")
    user_code = fields.Char()
    is_special_price = fields.Boolean()
    special_price = fields.Float()
    state = fields.Selection(TicketLineState.name_value())
    sync_id = fields.Integer(index=True)

    def action_edit_ticket_line(self):
        ...


class TicketLineUpdate(models.TransientModel):
    _inherit = "dt.ticket.line"
    _name = "dt.ticket.line.wizard"

    _description = "Ticket Lines Wizard"
