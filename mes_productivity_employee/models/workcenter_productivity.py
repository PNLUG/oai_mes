from odoo import models, fields


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    # new fields
    # emploees that does the work
    employee_ids = fields.Many2many(
        comodel_name="hr.employee",
        inverse_name="productivity_id",
        string="Employees",
        copy=True,
        )
