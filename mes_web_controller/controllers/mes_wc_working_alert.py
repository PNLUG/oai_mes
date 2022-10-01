# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http, _
from odoo.http import request
import pytz


class Main(http.Controller):
    @http.route(
        "/mes_wc_working/alert/",
        type="http",
        csrf=False,
        auth="user",
        website=True
        )
    def alert(self, **post):
        """
        _todo_
        POST parameters
        @param workcenter_id : id of the wc to extract
        @param productivity_id : id of the active productivity record _???_ giusto ?
        @param action : workcenter|block|wc_list|employees|alert_wo|unblock
        @param alert_id :
        @param loss_id : id of the loss type to set
        """

        # _todo_P_ manage error if

        action = post.get("action", False)
        user_tz = request.env.user.tz or str(pytz.utc.zone)
        local = pytz.timezone(user_tz)
        loss_id = post.get("loss_id", False)
        if loss_id:
            loss_id = int(loss_id)
        barcode = post.get("barcode3", False)
        wc_id = post.get("workcenter_id", False)
        wc = request.env["mrp.workcenter"].browse(int(wc_id ))

        if action == "wc_list":
            return http.local_redirect("/mes_wc_working/%s" % wc.department_id.id)
        if action == "workcenter":
            return http.local_redirect("/mes_wc_working/open_wos/%s" % wc_id)

        if wc_id:
            wc = request.env["mrp.workcenter"].browse(int(wc_id))
        else:
            return http.local_redirect("/mes_wc_working")

        if post.get("alert", False) == "employees":
            # show employee list
            productivity_id = post.get("productivity_id", False)
            productivity = request.env["mrp.workcenter.productivity"].browse(
                int(productivity_id)
                )
            values = {
                "title": "Employees",
                "productivity_id": productivity.id,
                "employees": productivity.employee_ids,
                }
            return request.render("mes_web_controller.employee_list", values)

        if barcode:
            try:
                # check if loss-id exists
                loss_id = int(barcode)
                loss = (
                    request.env["mrp.workcenter.productivity.loss"]
                    .browse(loss_id)
                    .exists()
                    )
                if not loss:
                    # _todo_ gestire messaggio eccezzione
                    raise Exception
            except Exception:
                alerts = request.env["mrp.workcenter.productivity.loss"].search(
                    [
                        ("loss_type", "=", "availability"),
                        # a standard i fermi sono ('manual', '=', 'true')
                    ],
                    limit=20,
                    order="name",
                    )
                values = {
                    "title": "Mobile Alert",
                    "alerts": alerts,
                    "workcenter": wc,
                    "error": _("Loss reference not found (code error)"),
                    }
                return request.render("mes_web_controller.workorder_alert", values)

        if loss_id:
            # record productivity loss
            wc.order_ids.end_all()
            employees = (
                request.env["mrp.workcenter.productivity"]
                .search(
                    [("workcenter_id", "=", wc.id)], order="date_start desc", limit=1
                )
                .employee_ids.mapped("employee_id")
                )
            productivity = request.env["mrp.workcenter.productivity"].create(
                {
                    "workcenter_id": wc.id,
                    "loss_id": loss_id,
                    "employee_ids": [(0, 0, {"employee_id": e}) for e in employees.ids],
                    "status": "stopped",
                }
                )
            time_start = productivity.date_start.astimezone(local)
            date_start_ms = time_start.timestamp() * 1000  # value to pass to jquery
            values = {
                "productivity": productivity,
                "workcenter": productivity.workcenter_id,
                "data_start_msec": date_start_ms,
                "employee_ids": productivity.employee_ids,
                }
            return request.render("mes_web_controller.workorder_alert", values)
        else:
            # show wo list
            wc.unblock()
            return http.local_redirect("/mes_wc_working/open_wos/" + str(wc_id))
