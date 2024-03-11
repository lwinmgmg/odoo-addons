from typing import List, Tuple
from enum import Enum
import requests
from odoo import fields, models, api

from ..utility.dt_formatter import remove_dt_tz
from ..datamodels.ticket import TicketData, TicketLineData

ODOO_TOKEN_TYPE = "Odoo"

def get_dt_header(model: models.Model) -> dict:
    token = model.env["res.users.api.user"].search([("audience", "=", "dt")])[0].encode()
    return {
            "content-type": "application/json",
            "Authorization": f"{ODOO_TOKEN_TYPE} {token}"
        }


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
    price = fields.Float()
    start_num = fields.Integer()
    end_num = fields.Integer()
    win_num = fields.Integer()
    start_date = fields.Datetime()
    end_date = fields.Datetime()
    available_count = fields.Integer()
    reserved_count = fields.Integer()
    sold_count = fields.Integer()
    line_ids = fields.One2many(comodel_name="dt.ticket.line", inverse_name="ticket_id")
    sync_id = fields.Integer(index=True)

    @api.onchange("start_num", "end_num")
    def _onchange_start_end_num(self):
        for record in self:
            record.available_count = 1 + self.end_num - self.start_num

    def construct_datamodel(self) -> TicketData:
        return TicketData.model_validate(self)

    def action_update_ticket(self):
        data = TicketData.model_validate(self, from_attributes=True)
        res = self.env["dt.ticket.wizard"].create(data.model_dump())
        return {
            "name": "Ticket Update",
            "type": "ir.actions.act_window",
            "res_model": "dt.ticket.wizard",
            "view_mode": "form",
            "view_id": self.env.ref(
                "dream_ticket_admin.view_dt_ticket_form_update_wizard"
            )[0].id,
            "res_id": res.id,
            "target": "new",
        }

    def action_refresh_ticket(self):
        self.search([]).unlink()
        url = "http://0.0.0.0:8000/graphql"
        payload = """
        query ticketQuery($user: String!){
            ticketQuery(query: {
                domain: [["sync_user", "=", $user]],
                order: {write_date: "desc"}
            }){
                id,
                name,
                state,
                description,
                startNum,
                price,
                endNum,
                startDate,
                endDate,
                winNum,
                availableCount,
                reservedCount,
                soldCount,
                createDate,
                writeDate
            }
        }
        """
        res = requests.post(
            url=url,
            json={"query": payload, "variables": {"user": self.env.user.login}},
            headers=get_dt_header(self),
        )
        data = res.json()
        self.create(
            [
                remove_dt_tz(TicketData.construct_from_gql(tkt).model_dump())
                for tkt in data.get("data").get("ticketQuery")
            ]
        )
        return self.env.ref("dream_ticket_admin.action_dt_ticket").read()[0]

    def action_refresh_ticket_lines(self):
        self.line_ids.unlink()
        url = "http://0.0.0.0:8000/graphql"
        payload = """
        query ticket($id: ID!){
            ticket(id: $id){
                lines{
                    id,
                    number,
                    userCode,
                    state,
                    isSpecialPrice,
                    specialPrice,
                    ticketId
                }
            }
        }
        """
        res = requests.post(
            url=url,
            json={"query": payload, "variables": {"id": self.sync_id}},
            headers=get_dt_header(self),
        )
        data_list = res.json()
        tickets: List[TicketLineData] = []
        for data in data_list["data"]["ticket"]["lines"]:
            data["ticketId"] = self.id
            tickets.append(TicketLineData.construct_from_gql(data=data))
        return self.env["dt.ticket.line"].create([tkt.model_dump() for tkt in tickets])

    def action_go_to_lines(self):
        if not self.line_ids:
            self.action_refresh_ticket_lines()
        return {
            "name": "Ticket Lines",
            "type": "ir.actions.act_window",
            "res_model": "dt.ticket.line",
            "view_mode": "tree,form",
            "domain": [("ticket_id", "=", self.id)],
        }


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

    _order = "number asc"

    number = fields.Integer()
    display_name = fields.Char(compute="_compute_display_name")
    ticket_id = fields.Many2one(comodel_name="dt.ticket", ondelete="cascade")
    user_code = fields.Char()
    is_special_price = fields.Boolean()
    special_price = fields.Float()
    state = fields.Selection(TicketLineState.name_value())
    sync_id = fields.Integer(index=True)

    def _compute_display_name(self):
        for record in self:
            record.display_name = f"Number : {record.number}"

    def action_edit_ticket_line(self):
        data = TicketLineData(
            sync_id=self.sync_id,
            ticket_id=self.ticket_id.id,
            number=self.number,
            state=self.state,
            user_code=self.user_code or "",
            is_special_price=self.is_special_price,
            special_price=self.special_price
        )
        res = self.env["dt.ticket.line.wizard"].create(data.model_dump())
        return {
            "name": "Ticket Line Update",
            "type": "ir.actions.act_window",
            "res_model": "dt.ticket.line.wizard",
            "view_mode": "form",
            "view_id": self.env.ref(
                "dream_ticket_admin.view_dt_ticket_line_form_update_wizard"
            )[0].id,
            "res_id": res.id,
            "target": "new",
        }
