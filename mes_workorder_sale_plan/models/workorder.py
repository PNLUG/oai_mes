from odoo import models, fields


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    # new fields
    # reference to mrp sale plan
    plan_id = fields.Many2one(
        omodel_name="mrp.sale.plan",
        string="_todo_",
        )
