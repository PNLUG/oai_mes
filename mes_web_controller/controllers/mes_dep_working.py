# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http
from odoo.http import request


class Main(http.Controller):
    def department_active(self):
        """
        returns departments with open workorders
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
        return dprtmts

    @http.route(
        "/mes_dep_working/",
        type="http",
        csrf=False,
        auth="user",
        website=True
        )
    def department(self, **post):
        """
        show departments with workorders to do
        """
        dprtmts = self.department_active()
        values = {
            "dprtmts": dprtmts,
            }
        if request.session.get('error'):
            values['error'] = request.session.get('error')
        request.session.update({'error':False})
        return request.render("mes_web_controller.department_working", values)
