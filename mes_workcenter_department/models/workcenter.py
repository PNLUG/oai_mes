from odoo import models, fields


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    # new fields
    # department
    department_id = fields.Many2one(
        comodel_name="hr.department",
        copy=True,
        )
