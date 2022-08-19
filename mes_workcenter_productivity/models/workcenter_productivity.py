from odoo import models, fields


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    # _todo_ trovare vistra productivity e visualizzare campi nuovi

    # new fields
    # >>>
    # _???_ sono già definiti in OCB, li recupera per averli a disposizione?

    production_id = fields.Many2one(
        string="Production",
        store=True,
        related="workorder_id.production_id",
        )

    # product to produce
    product_id = fields.Many2one(
        string="Product",
        store=True,
        related="workorder_id.product_id",
        )
    # operation to do
    operation_id = fields.Many2one(
        string="Operation",
        store=True,
        related="workorder_id.operation_id",
        )
    # _todo _
    categ_id = fields.Many2one(
        string="Product Categ",
        store=True,
        related="workorder_id.product_id.categ_id",
        )
    # <<<

    # qty done
    # _???_ a cosa serve se c'è nel WO?
    qty_produced = fields.Float(
        string="Qty Produced",
        default=0.0,
        readonly=False,
        copy=False,
        )

    # qty scraped
    qty_scrap = fields.Float(
        string="Qty Scrap",
        default=0.0,
        readonly=False,
        copy=False,
        )
    # status of production
    # _todo_ meglio cambiate nome? status; Block=>Blocked / Stopped?
    action = fields.Selection(
        [("working", "Working"),
         ("setup", "Setup"),
         ("block", "Block"),
         ],
        default="working",
        )
