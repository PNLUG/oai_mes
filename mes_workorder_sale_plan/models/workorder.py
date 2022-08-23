from odoo import models, fields


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    # _todo_ estendere vista per visualizzare campo

    # new fields
    # reference to mrp sale plan
    plan_id = fields.Many2one(
        comodel_name="mrp.sale.plan",
        string="_todo_",
        )
