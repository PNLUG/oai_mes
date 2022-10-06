from odoo import models, fields


class MrpWorkcenter(models.Model):
    _inherit = "hr.department"

    # new fields
    # open workorder
    open_wo = fields.Integer(
        string="Open WO",
        )
