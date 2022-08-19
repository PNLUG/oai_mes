# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http, _
from odoo.http import request
import pytz


class Main(http.Controller):
    @http.route(
        "/mobile_mrp_working/wo/",
        type="http",
        csrf=False,
        auth="user",
        website=True
        )
    def workorder(self, **post):
        """
        _todo_
        shows wo details based on selection
        @param btn : block|back|barcode|search
        @param wc_id
        @param barcode2
        @param start_wo
        @param search2
        """
        user_tz = request.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        values = {}
        workcenter_id = post.get("wc_id", False)
        wc_id = int(workcenter_id)
        wc = request.env["mrp.workcenter"].browse(wc_id)
        barcode2 = post.get("barcode2", False)

        # manage options selected
        if post.get("btn", False) == "back":
            # goes to main page
            return http.local_redirect("/mobile_mrp_working")
        elif barcode2 or post.get("btn", False) == "barcode":
            # set active wo
            wo_id = barcode2
            values["action"] = "working"
        elif post.get("btn", False) == "block":
            # _???_ stop wo production
            workcenter_id = post.get("wc_id", False)
            wc_id = int(workcenter_id)
            wc = request.env["mrp.workcenter"].browse(wc_id)
            alerts = request.env["mrp.workcenter.productivity.loss"].search(
                [("loss_type", "=", "availability")],
                limit=20,
                order="name",
                )
            values = {
                "title": "Mobile Alert",
                "alerts": alerts,
                "workcenter": wc,
                "action": "block",
                # "employee_ids": False _todo_ passare gli employee del productivity
                # precedente?
                }
            return request.render("mn_web_controller.alert_list", values)
        elif post.get("start_wo", False):
            # set wo working status
            wo_id = post.get("start_wo", False)
            values["action"] = "working"
        elif post.get("setup_wo", False):
            # set wo setup status
            wo_id = post.get("setup_wo", False)
            values["action"] = "setup"
        elif post.get("btn", False) == "search" or post.get("search2", False):
            # _todo_
            wos = request.env["mrp.workorder"]
            search2 = post.get("search2", False)
            domain = [
                ("workcenter_id", "=", wc_id),
                ("state", "not in", ["done", "cancel"]),
                ]
            if not search2:
                wos = request.env["mrp.workorder"].search(
                    domain,
                    limit=200,
                    order="date_planned_start",
                    )
            if search2:
                # search by plan
                domain1 = domain.copy()
                domain1.append(("plan_id", "ilike", search2))
                values["search2"] = search2
                wos = request.env["mrp.workorder"].search(
                    domain1,
                    limit=200,
                    order="date_planned_start",
                    )
                if not wos:
                    # search by product
                    domain2 = domain.copy()
                    domain2.append(("product_id", "ilike", search2))
                    wos = request.env["mrp.workorder"].search(
                        domain2,
                        limit=200,
                        order="date_planned_start",
                        )
                if not wos:
                    # search by sale order
                    domain3 = domain.copy()
                    domain3.append(("sale_id", "ilike", search2))
                    wos = request.env["mrp.workorder"].search(
                        domain3,
                        limit=200,
                        order="date_planned_start",
                        )
                if not wos:
                    # search by sale order _???_ search by client
                    domain4 = domain.copy()
                    domain4.append(("sale_id.client_order_ref", "ilike", search2))
                    wos = request.env["mrp.workorder"].search(
                        domain4,
                        limit=200,
                        order="date_planned_start",
                        )
                if not wos:
                    # search by production order
                    domain5 = domain.copy()
                    domain5.append(("production_id", "ilike", search2))
                    wos = request.env["mrp.workorder"].search(
                        domain5,
                        limit=200,
                        order="date_planned_start",
                        )
            values.update(
                {
                    "title": "Workorder for Workcenter",
                    "wc": wc,
                    "wos": wos,
                }
                )
            return request.render("mn_web_controller.workorder_list", values)
        else:
            # goes to main page
            return http.local_redirect("/mobile_mrp_working/")

        # serch wo
        try:
            wo = request.env["mrp.workorder"].browse(int(wo_id))
            if not wo.state or wo.state in ["done", "cancel"]:
                raise Exception
        except request.exceptions:
            # _todo_ verificare se except request.exceptions: va bene
            wos = request.env["mrp.workorder"].search(
                [
                    ("workcenter_id", "=", wc_id),
                    ("state", "not in", ["done", "cancel"]),
                ],
                limit=200,
                order="date_planned_start",
                )
            values = {
                "title": "Workorder for Workcenter",
                "wc": wc,
                "wos": wos,
                "error": _("ERROR: Barcode not found"),
                }
            return request.render("mn_web_controller.workorder_list", values)

        # _todo_ descrivere condizione
        # _???_ use last employee productivity
        values["wo"] = wo
        values["workcenter"] = wo.workcenter_id

        # retrieve employees last productivity
        employees = (
            request.env["mrp.workcenter.productivity"]
            .search([("workcenter_id", "=", wc.id)], order="date_start desc", limit=1)
            .employee_ids.mapped("employee_id")
            )
        # _???_ cosa fa questo comando
        wo.button_start()
        productivity = request.env["mrp.workcenter.productivity"].search(
            [
                ("workcenter_id", "=", wo.workcenter_id.id),
                ("workorder_id", "=", wo.id),
                ("date_end", "=", False),
            ],
            limit=1,
            order="id desc",
            )
        productivity.write(
            {
                "employee_ids": [(0, 0, {"employee_id": e}) for e in employees.ids],
                "action": values["action"],
                # _todo_ aggiornare loss_id / loss_type
            }
            )

        time_start = productivity.date_start.astimezone(local)
        date_start_ms = time_start.timestamp() * 1000  # value to pass to jquery
        values["title"] = "Workorder for Workcenter"
        values["productivity"] = productivity
        values["data_start_msec"] = date_start_ms
        return request.render("mn_web_controller.workorder_details", values)
