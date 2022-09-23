# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http
from odoo.http import request


class Main(http.Controller):
    @http.route(
        "/mes_wc_working/",
        type="http",
        csrf=False,
        auth="user",
        website=True
        )
    def main(self, **post):
        """
        show workcenter with workorder to do
        """
        wcs = request.env["mrp.workcenter"].search(
            [("count_open_wo", "!=", 0)],
            order="name",
            )
        values = {
            "wcs": wcs,
            }
        return request.render("mes_web_controller.workcenter_working", values)
