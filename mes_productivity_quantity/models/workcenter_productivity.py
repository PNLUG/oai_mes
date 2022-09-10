from odoo import models, fields


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    # _todo_ trovare vistra productivity e visualizzare campi nuovi
    # _todo_ verificare come vengono alimentati

    # new fields
    # qty done
    # _???_ a cosa serve se c'è nel WO?
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
