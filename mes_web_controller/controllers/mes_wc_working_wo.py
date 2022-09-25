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
        @param action : block|back|viewwo|search
        @param wc_id : id of the workcenter
        @param view_wo : id of the wo to view
        @param start_wo : id of the wo to start
        @param setup_wo : id of the wo to setup
        @param search_wo : id of the wo to search
        @param search_wide : string to use to search wos
        """

        user_tz = request.env.user.tz or str(pytz.utc.zone)
        local = pytz.timezone(user_tz)
        action = post.get("action", False)
        wc_id = int(post.get("wc_id", False))
        wc = request.env["mrp.workcenter"].browse(wc_id)
        wo_id = False
        view_wo = post.get("view_wo", False)
        start_wo = post.get("start_wo", False)
        setup_wo = post.get("setup_wo", False)
        search_wo = post.get("search_wo", False)
        search_wide = post.get("search_wide", False)
        values = {}
        productivity = request.env["mrp.workcenter.productivity"]
        date_start_ms = ''

        if action == "back" \
           and (not search_wo or search_wo == "") \
           and (not search_wide or search_wide == ""):
            # goes to main view
            return http.local_redirect("/mes_wc_working")

        if workorder_id:
            # check wo id and set related wc
            try:
                wo_id = workorder_id
                wc = request.env["mrp.workorder"].browse(wo_id).workcenter_id
                wc_id = wc.id
            except Exception:
                wcs = request.env["mrp.workcenter"].search(
                    [("count_open_wo", "!=", 0)],
                    order="name",
                    )
                values = {
                    "wcs": wcs,
                    "error": _("Error: Workorder ID %d not found" % workorder_id),
                    }
                return request.render("mes_web_controller.workcenter_working", values)

        # manage options selected
        if view_wo:
            wo_id = view_wo
        elif start_wo:
            # set wo working status
            wo_id = start_wo
            values = {
                "loss_state_id": "working",
                }
        elif setup_wo:
            # set wo setup status
            wo_id = setup_wo
            values = {
                "loss_state_id": "preparation",
                }
        elif action == "block":
            # stop wo production
            # _???_ chiarire a cosa serve il dato alerts
            alerts = request.env["mrp.workcenter.productivity.loss"].search(
                [("loss_type", "=", "availability")],
                limit=20,
                order="name",
                )
            values = {
                "alerts": alerts,
                "workcenter": wc,
                "loss_state_id": "stopped",
                # "employee_ids": False _todo_P_ passare gli employee del productivity
                # precedente?
                }
            return request.render("mes_web_controller.workorder_alert", values)
        elif action == "search" or search_wide:
            # try to find wo based on search string
            wos = request.env["mrp.workorder"]
            # set base domain filter
            domain = [
                ("workcenter_id", "=", wc_id),
                ("state", "not in", ["done", "cancel"]),
                ]
            if not search_wide:
                wos = request.env["mrp.workorder"].search(
                    domain,
                    limit=200,
                    order="date_planned_start",
                    )
            if search_wide:
                # search by plan
                domain1 = domain.copy()
                domain1.append(("plan_id", "ilike", search_wide))
                values["search_wide"] = search_wide
                wos = request.env["mrp.workorder"].search(
                    domain1,
                    limit=200,
                    order="date_planned_start",
                    )
                if not wos:
                    # search by product
                    domain2 = domain.copy()
                    domain2.append(("product_id", "ilike", search_wide))
                    wos = request.env["mrp.workorder"].search(
                        domain2,
                        limit=200,
                        order="date_planned_start",
                        )
                if not wos:
                    # search by sale order
                    domain3 = domain.copy()
                    domain3.append(("sale_id", "ilike", search_wide))
                    wos = request.env["mrp.workorder"].search(
                        domain3,
                        limit=200,
                        order="date_planned_start",
                        )
                if not wos:
                    # search by client sale order ref
                    domain4 = domain.copy()
                    domain4.append(("sale_id.client_order_ref", "ilike", search_wide))
                    wos = request.env["mrp.workorder"].search(
                        domain4,
                        limit=200,
                        order="date_planned_start",
                        )
                if not wos:
                    # search by production order
                    domain5 = domain.copy()
                    domain5.append(("production_id", "ilike", search_wide))
                    wos = request.env["mrp.workorder"].search(
                        domain5,
                        limit=200,
                        order="date_planned_start",
                        )
            # show result list
            values.update({
                    "wc": wc,
                    "wos": wos,
                    })
            return request.render("mes_web_controller.workorder_list", values)
        else:
            # goes to wo list of the wc
            return http.local_redirect(("/mes_wc_working/open_wos/%d" % wc_id))

        # extract wo based on wo_id selected
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
                "wc": wc,
                "wos": wos,
                "error": _("Error: Workorder ID %d not found for this Workcenter"
                           % int(wo_id)),
                }
            return request.render("mes_web_controller.workorder_list", values)

        # _todo_ descrivere condizione
        # _???_ uses last employee productivity
        values["wo"] = wo
        values["workcenter"] = wo.workcenter_id

        # retrieves employees of last productivity
        employees = (
            request.env["mrp.workcenter.productivity"].search(
                [("workcenter_id", "=", wc.id)],
                order="date_start desc",
                limit=1,
                ).employee_ids
            )

        if view_wo:
            # get the last productivity info to show
            productivity = request.env["mrp.workcenter.productivity"].search(
                [
                    ("workcenter_id", "=", wo.workcenter_id.id),
                    ("workorder_id", "=", wo.id),
                ],
                limit=1,
                order="id desc",
                )
        if start_wo:
            # start wo production
            wo.button_start()
            # get the last productivity not completed
            productivity = request.env["mrp.workcenter.productivity"].search(
                [
                    ("workcenter_id", "=", wo.workcenter_id.id),
                    ("workorder_id", "=", wo.id),
                    ("date_end", "=", False),
                ],
                limit=1,
                order="id desc",
                )
            values["data_start_msec"] = date_start_ms

        # _???_ verificare questa azione
        productivity.write({
                "employee_ids": [(0, 0, {"employee_id": e}) for e in employees.ids],
                # _todo_P_ aggiornare loss_id / loss_type
                })

        time_start = productivity.date_start.astimezone(local)
        date_start_ms = time_start.timestamp() * 1000
        values["productivity"] = productivity

        return request.render("mes_web_controller.workorder_details", values)
