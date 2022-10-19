# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http
from odoo.http import request


class Main(http.Controller):
    @http.route(
        [
            "/mes_wc_working/<department_id>",
            "/mes_wc_working/",
        ],
        type="http",
        csrf=False,
        auth="user",
        website=True
        )
    def main(self, department_id=None, **post):
        """
        show workcenter with workorder to do
        """
        department_id = department_id or False
        wcs = request.env["mrp.workcenter"].search([
                ("count_open_wo", "!=", 0),
                ("department_id", "=", int(department_id)),
            ],
            order="name",
            )
        dep = request.env["hr.department"].browse(int(department_id))
        values = {
            "dep": dep,
            "wcs": wcs,
            }
        if request.session.get('error'):
            values['error'] = request.session.get('error')
            request.session.update({'error': False})

        return request.render("mes_web_controller.workcenter_working", values)
