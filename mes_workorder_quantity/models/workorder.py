from odoo import models, fields


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    # _todo_ estendere vista on il campo

    # new fields
    # qty produced
    qty_produced = fields.Float(
        string="Qty Produced",
        default=0.0,
        readonly=False,
        copy=False,
        )
