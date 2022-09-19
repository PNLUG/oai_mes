# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http, _
from odoo.http import request
import pytz


class Main(http.Controller):
    @http.route(
        [
            "/mes_wc_working/wo/<workorder_id>",
            "/mes_wc_working/wo/",
        ],
        type="http",
        csrf=False,
        auth="user",
        website=True,
        )
    def workorder(self, workorder_id=None, **post):
        """
        _todo_
        shows wo details based on selection
        POST parameters:
        @param action : block|back|openwo|search
        @param wc_id
        @param wo_id
        @param start_wo : id of the wo to start
        @param setup_wo : id of the wo to setup
        @param widesearch
        """

        user_tz = request.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        action = post.get("action", False)
        wc_id = int(post.get("wc_id", False))
        wc = request.env["mrp.workcenter"].browse(wc_id)
        wo_id = post.get("wo_id", False)
        view_wo = post.get("view_wo", False)
        start_wo = post.get("start_wo", False)
        setup_wo = post.get("setup_wo", False)
        widesearch = post.get("widesearch", False)
        values = {}
        productivity = request.env["mrp.workcenter.productivity"]
        date_start_ms = False

        if post.get("action", False) == "back" \
           and (not wo_id or wo_id == "") \
           and (not widesearch or widesearch == ""):
            # goes to main view
            return http.local_redirect("/mes_wc_working")

        if workorder_id:
            view_wo = workorder_id
            try:
                wc = request.env["mrp.workorder"].browse(int(view_wo)).workcenter_id
                wc_id = wc.id
            except Exception:
                wcs = request.env["mrp.workcenter"].search(
                    [("count_open_wo", "!=", 0)],
                    order="name",
                    )
                values = {
                    "title": "Workorder loaded",
                    "wcs": wcs,
                    "error": _("ERROR: Workorder ID %d not found" % int(view_wo)),
                    }
                return request.render("mes_web_controller.workcenter_working", values)

        # manage options selected
        if wo_id or action == "openwo":
            # set active wo
            values["loss_state_id"] = "working"
        elif view_wo:
            wo_id = view_wo
        elif action == "block":
            # _???_ stop wo production
            alerts = request.env["mrp.workcenter.productivity.loss"].search(
                [("loss_type", "=", "availability")],
                limit=20,
                order="name",
                )
            values = {
                "title": "Mobile Alert",
                "alerts": alerts,
                "workcenter": wc,
                "loss_state_id": "stopped",
                # "employee_ids": False _todo_ passare gli employee del productivity
                # precedente?
                }
            return request.render("mn_web_controller.alert_list", values)
        elif start_wo:
            # set wo working status
            wo_id = start_wo
            values["loss_state_id"] = "working"
        elif setup_wo:
            # set wo setup status
            wo_id = setup_wo
            values["loss_state_id"] = "preparation"
        elif action == "search" or widesearch:
            # _todo_
            wos = request.env["mrp.workorder"]
            domain = [
                ("workcenter_id", "=", wc_id),
                ("state", "not in", ["done", "cancel"]),
                ]
            if not widesearch:
                wos = request.env["mrp.workorder"].search(
                    domain,
                    limit=200,
                    order="date_planned_start",
                    )
            if widesearch:
                # search by plan
                domain1 = domain.copy()
                domain1.append(("plan_id", "ilike", widesearch))
                values["widesearch"] = widesearch
                wos = request.env["mrp.workorder"].search(
                    domain1,
                    limit=200,
                    order="date_planned_start",
                    )
                if not wos:
                    # search by product
                    domain2 = domain.copy()
                    domain2.append(("product_id", "ilike", widesearch))
                    wos = request.env["mrp.workorder"].search(
                        domain2,
                        limit=200,
                        order="date_planned_start",
                        )
                if not wos:
                    # search by sale order
                    domain3 = domain.copy()
                    domain3.append(("sale_id", "ilike", widesearch))
                    wos = request.env["mrp.workorder"].search(
                        domain3,
                        limit=200,
                        order="date_planned_start",
                        )
                if not wos:
                    # search by client sale order ref
                    domain4 = domain.copy()
                    domain4.append(("sale_id.client_order_ref", "ilike", widesearch))
                    wos = request.env["mrp.workorder"].search(
                        domain4,
                        limit=200,
                        order="date_planned_start",
                        )
                if not wos:
                    # search by production order
                    domain5 = domain.copy()
                    domain5.append(("production_id", "ilike", widesearch))
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
            return request.render("mes_web_controller.workorder_list", values)
        else:
            # goes to main page
            return http.local_redirect(("/mes_wc_working/open_wos/%d" % wc_id))

        # serch wo
        try:
            wo = request.env["mrp.workorder"].search([
                ('workcenter_id', '=', wc_id),
                ('id', '=', int(wo_id))
                ])
            if not wo.state or wo.state in ["done", "cancel"]:
                raise Exception
        except Exception:
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
                "error": _("ERROR: Workorder ID %d not found for this Workcenter"
                           % int(wo_id)),
                }
            return request.render("mes_web_controller.workorder_list", values)

        # _todo_ descrivere condizione
        # _???_ use last employee productivity
        values["wo"] = wo
        values["workcenter"] = wo.workcenter_id

        # retrieve employees last productivity
        employees = (
            request.env["mrp.workcenter.productivity"]
            .search([("workcenter_id", "=", wc.id)], order="date_start desc", limit=1)
            .employee_ids
            )

        # show wo info
        if view_wo:
            productivity = request.env["mrp.workcenter.productivity"].search(
                [
                    ("workcenter_id", "=", wo.workcenter_id.id),
                    ("workorder_id", "=", wo.id),
                ],
                limit=1,
                order="id desc",
                )
        # start wo production
        if start_wo:
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
            time_start = productivity.date_start.astimezone(local)
            date_start_ms = time_start.timestamp() * 1000  # value to pass to jquery

        # _???_ verificare questa azione
        productivity.write(
            {
                "employee_ids": [(0, 0, {"employee_id": e}) for e in employees.ids],
            }
            )
        values["title"] = "Workorder for Workcenter"
        values["productivity"] = productivity
        values["data_start_msec"] = date_start_ms
        return request.render("mes_web_controller.workorder_details", values)
