# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http, _
from odoo.http import request
import pytz


class Main(http.Controller):
    @http.route(
        "/mes_wc_working/employees/",
        type="http",
        csrf=False,
        auth="user",
        website=True,
        )
    def employees(self, **post):
        """
        _todo_
        @param productivity_id :
        @param barcode : employee_id to register
        @param btn : back|add
        @param delete : employee_id to delete
        """
        user_tz = request.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        productivity_id = post.get("productivity_id", False)

        if not productivity_id:
            return http.local_redirect("/mobile_mrp_working")

        barcode = post.get("barcode", False)
        productivity = request.env["mrp.workcenter.productivity"].browse(
            int(productivity_id)
            )
        values = {}

        if post.get("btn", False) == "back":
            # goes to stop or wo details
            time_start = productivity.date_start.astimezone(local)
            date_start_ms = time_start.timestamp() * 1000  # value to pass to jquery
            values = {
                "data_start_msec": date_start_ms,
                "title": "Mobile working",
                "productivity": productivity,
                "workcenter": productivity.workcenter_id,
                "wo": productivity.workorder_id,
                "status": productivity.loss_id.loss_state,
                "employee_ids": productivity.employee_ids,
                }
            if productivity.action == "block":
                return request.render("mes_web_controller.alert_list", values)
            else:
                return request.render("mes_web_controller.workorder_details", values)

        elif post.get("btn", False) == "add":
            # check and add employee to productivity
            if barcode:  # BARCODE = ID EMPLOYEE
                try:
                    employee_id = int(barcode)
                    if request.env["hr.employee"].browse(employee_id).exists():
                        if (
                            employee_id
                            in productivity.employee_ids.mapped("id")
                            # _???_ verificare logica controllo
                        ):
                            values["error"] = _("User already present")
                        else:
                            productivity.write(
                                #{"employee_ids": [(0, 0, {"employee_id": employee_id})]}
                                {"employee_ids": employee_id}
                            )
                    else:
                        values["error"] = _("Employee id not found (barcode error)")
                except Exception:
                    # _todo_ verificare se except request.exceptions: va bene
                    values["error"] = _("Employee id not found (barcode error)")
        elif post.get("delete", False):
            # delete employee_id productivity
            employee_id = int(post.get("delete"))
            productivity.write({"employee_ids": [(2, employee_id)]})
        values.update(
            {
                "title": "Employees",
                "productivity_id": productivity_id,
                "employees": productivity.employee_ids,
            }
        )
        return request.render("mes_web_controller.employee_list", values)
