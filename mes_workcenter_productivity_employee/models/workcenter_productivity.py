from odoo import models, fields


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    # new fields
    # emploee that does the work
    employee_ids = fields.One2many(
        comodel_name="mrp.workcenter.productivity.employee",
        inverse_name="productivity_id",
        string="Employees",
        copy=True,
        )

    # _???_ tentativo di agganciare direttamente employee
    xemployee_ids = fields.One2many(
        comodel_name="hr.employee",
        inverse_name="productivity_id",
        string="Employees",
        copy=True,
        )


class HrEmployee(models.Model):
    # _todo_ tentativo di agganciare direttamente employee
    _inherit = "hr.employee"

    productivity_id = fields.Many2one(
        comodel_name="mrp.workcenter.productivity",
        string="Productivity",
        index=True,
        ondelete="cascade",
        required=True,
    )
