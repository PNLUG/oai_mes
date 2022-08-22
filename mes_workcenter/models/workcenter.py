from odoo import models, fields


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
    # wo to complete
    count_open_wo = fields.Integer(
        string="Open Workorders",
        help="Workorders in status different than done and cancel",
        compute="_compute_count_open_wo",
        default=0,
        )
