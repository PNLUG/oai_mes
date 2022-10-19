# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http
from odoo.http import request


class Main(http.Controller):
    @http.route(
        "/mes_wo_open/<department_id>",
        type="http",
        csrf=False,
        auth="user",
        website=True
        )
    def main(self, department_id=None, **post):
        """
        show open workorders of workcenters associated to a department
        """
        department_id = int(department_id) if department_id else False

        dep = request.env["hr.department"].browse(department_id)

        wos_open = request.env["mrp.workorder"].search([
            ("workcenter_id", "!=", False),
            ("workcenter_id.department_id", "=", department_id),
            ],
            order="date_planned_start",
            )

        values = {
            "wos_open": wos_open,
            "department": dep,
            }
        if request.session.get('error'):
            values['error'] = request.session.get('error')
            request.session.update({'error': False})
        return request.render("mes_web_controller.wo_open", values)
