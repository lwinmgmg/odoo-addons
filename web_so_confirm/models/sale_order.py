from odoo import fields, models

class SaleOrder(models.Model):
    NAME = "sale.order"
    _inherit = NAME

    unique_ref = fields.Char("Unique Reference", index=True, track_visibility='onchange')

    _sql_constraints = [
        ('unique_ref_unique', 'unique (unique_ref)', "Can't be used old Unique Reference"),
    ]
