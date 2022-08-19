# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http, _
from odoo.http import request
import pytz


class Main(http.Controller):
    @http.route(
        "/mobile_mrp_working/alert/",
        type="http",
        csrf=False,
        auth="user",
        website=True
        )
    def alert(self, **post):
        """
        _todo_
        @param loss_id :
        @param barcode3 : loss_id
        @param workcenter_id :
        @param productivity_id :
        @param btn :
        """
        # _todo_ manage error if
        user_tz = request.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        loss_id = post.get("loss_id", False)
        if loss_id:
            loss_id = int(loss_id)
        barcode = post.get("barcode3", False)
        wc_id = post.get("workcenter_id", False)

        if wc_id:
            wc = request.env["mrp.workcenter"].browse(int(wc_id))
        else:
            return http.local_redirect("/mobile_mrp_working")

        if post.get("btn", False) == "employees":
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
            return request.render("mn_web_controller.employee_list", values)

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
                    raise Exception
            except request.exceptions:
                # _todo_ verificare se except request.exceptions: va bene
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
                    "error": _("Loss reference not found (barcode error)"),
                    }
                return request.render("mn_web_controller.alert_list", values)

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
                    "action": "block",
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
            return request.render("mn_web_controller.alert_list", values)
        else:
            # show wo list
            wc.unblock()
            return http.local_redirect("/mobile_mrp_working/open_wos/" + str(wc_id))
