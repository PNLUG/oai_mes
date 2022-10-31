from odoo import models, fields


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    # new fields
    # employees that does the work
    employee_ids = fields.Many2many(
        comodel_name="hr.employee",
        string="Employees",
        copy=True,
        )
