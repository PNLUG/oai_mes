from logging import raiseExceptions
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"
    _description = "Count Open Workorder"

    def _compute_count_open_wo(self):
        """
        compute wo to complete for all workcenters
        """
        for wc in self:
            wc.count_open_wo = self.env["mrp.workorder"].search_count(
                [
                    ("workcenter_id", "=", wc.id),
                    ("state", "not in", ["done", "cancel"]),
                ],
            )

    # new fields
    # reference to parent workcenter
    parent_id = fields.Many2one(
        comodel_name="mrp.workcenter",
        string="Parent Workcenter",
        )
    # wo to complete
    count_open_wo = fields.Integer(
        string="Open Workorders",
        help="Workorders in status different than done and cancel",
        compute="_compute_count_open_wo",
        default=0,
        )

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        """
        avoid using self as parent
        """
        # _todo_ verificare se metodo corretto
        # _???_ self.id non mostra id corretto
        if self.ids[0] == self.parent_id.id:
            raise UserError(_("Not use itself as parent workcenter!"))

    def write(self, values):
        if self.id == values['parent_id']:
            raise UserError(_("Not use itself as parent workcenter!"))
        else:
            super().write(values)
