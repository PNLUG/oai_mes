from odoo import models, fields


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    # _todo_ estendere vista per visualizzare campo
    # _todo_ estendere mes_web_controller.workorder_list

    # new fields
    # reference to mrp sale plan
    plan_id = fields.Many2one(
        comodel_name="mrp.sale.plan",
        string="_todo_",
        )
