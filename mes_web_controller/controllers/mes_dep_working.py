# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http
from odoo.http import request


class Main(http.Controller):
    @http.route(
        "/mes_dep_working/",
        type="http",
        csrf=False,
        auth="user",
        website=True
        )
    def main(self, **post):
        """
        show departments with workorders to do
        """
        dprtmts = request.env["hr.department"].search([
            ("workcenter_ids", "!=", False),
            ("workcenter_ids.count_open_wo", "!=", 0),
            ],
            order="name",
            )

        for dep in dprtmts:
            wcs = request.env["mrp.workcenter"].search([
                ("count_open_wo", "!=", 0),
                ("department_id", "=", dep.id),
                ])
            dep.open_wo = sum(wc.count_open_wo for wc in wcs)
        values = {
            "dprtmts": dprtmts,
            }
        return request.render("mes_web_controller.department_working", values)
