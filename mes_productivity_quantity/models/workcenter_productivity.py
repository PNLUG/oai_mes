from odoo import models, fields


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    # _todo_ verificare come vengono alimentati => da metodi controller

    # new fields
    # qty done
    qty_produced = fields.Float(
        string="Qty Produced",
        default=0.0,
        readonly=False,
        copy=False,
        )
    # qty scraped
    qty_scraped = fields.Float(
        string="Qty Scraped",
        default=0.0,
        readonly=False,
        copy=False,
        )
