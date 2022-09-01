from odoo import models, fields


class ProductivityEmployees(models.Model):
    """
    associate an enploee to a production _todo_ guisto?
    """
    _name = "mrp.workcenter.productivity.employee"
    _rec_name = "employee_id"

    # emploee that does the work
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        )
    # production reference
    productivity_id = fields.Many2one(
        comodel_name="mrp.workcenter.productivity",
        string="Productivity",
        index=True,
        ondelete="cascade",
        required=True,
    )
