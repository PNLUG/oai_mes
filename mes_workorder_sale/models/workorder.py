from odoo import models, fields


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    # _todo_ creare vista per visualizzare il campo

    # new fields
    # reference to sale order _todo_ verificare modulo OCA mrp_sale_info
    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="_todo_",
        )
