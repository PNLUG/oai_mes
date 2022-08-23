from odoo import models, fields


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    # _todo_ estendere vista per visualizzare campo

    # new fields
    # emploee that does the work
    employee_ids = fields.One2many(
        comodel_name="mrp.workcenter.productivity.employee",
        inverse_name="productivity_id",
        string="Employees",
        copy=True,
        )
