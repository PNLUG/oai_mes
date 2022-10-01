from odoo import models, fields


class MrpWorkcenter(models.Model):
    _inherit = "hr.department"

    # new fields
    # department
    workcenter_ids = fields.One2many(
        comodel_name="mrp.workcenter",
        inverse_name="department_id",
        copy=False,
        )
