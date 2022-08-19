from odoo import models, fields


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    # new fields
    # reference to sale order _todo_ modulo a parte?
    sale_id = fields.Many2one(
        omodel_name="sale.order",
        string="_todo_",
        )

