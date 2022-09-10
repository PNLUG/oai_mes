from odoo import models, fields


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    # new fields
    # qty produced
    qty_produced = fields.Float(
        string="Qty produced",
        default=0.0,
        readonly=False,
        copy=False,
        )

    '''
    _todo_
    aggiungere quantità scartata
    aggiungere metodi di alimentazione da productivity
    '''
