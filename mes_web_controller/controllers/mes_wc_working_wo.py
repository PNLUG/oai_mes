# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http, _
from odoo.http import request
import pytz


class Main(http.Controller):

    def wo_wide_search(self, search_where, search_val, domain):
        """
        _todo_
        search workorder with a string contained in one of different attributes
        @param search_where list : coded attribute to search in
            'product'|'po'
        @param search_val string : text to search
        @param domain domain : enviroment filter
        """

        # set or operator for all the extends
        domain.extend(['|', '|'])

        if 'product' in search_where:
            # search by product
            domain.extend([
                ("product_id", "ilike", search_val),
                ("product_id.name", "ilike", search_val),
                ])
        if 'po' in search_where:
            # search by production order
            domain.extend([
                ("production_id", "ilike", search_val)
                ])

        wos = request.env["mrp.workorder"].search(
            domain,
            limit=200,
            order="date_planned_start",
            )
        return wos

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
        @param action : block|back|search_wo|search_wide
        @param dep_id : id of the department
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
        dep_id = request.session.get('dep_id')
        dep_id = dep_id if dep_id else post.get("dep_id", False)
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

        if view_wo:
            workorder_id = int(view_wo)
        if workorder_id:
            view_wo = workorder_id

        if action == "back" \
           and (not search_wo or search_wo == "") \
           and (not search_wide or search_wide == ""):
            # goes to main view
            return http.local_redirect("/mes_wc_working/%s" % wc.department_id.id)

        if workorder_id:
            # check wo id and set related wc
            try:
                wo_id = int(workorder_id)
                wc = request.env["mrp.workorder"].browse(wo_id).workcenter_id
                wc_id = wc.id
            except Exception:
                if dep_id:
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
                        "error": _(
                            "Error: Workorder ID %d not found" % int(workorder_id)),
                        }
                    return request.render(
                        "mes_web_controller.department_working", values
                        )
                else:
                    wcs = request.env["mrp.workcenter"].search(
                        [("count_open_wo", "!=", 0)],
                        order="name",
                        )
                    values = {
                        "wcs": wcs,
                        "error": _(
                            "Error: Workorder ID %d not found" % int(workorder_id)),
                        }
                    return request.render(
                        "mes_web_controller.workcenter_working", values
                        )

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
        elif action == "search_wo" or search_wide:
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
                wos = self.wo_wide_search(['product', 'po'], search_wide, domain)
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

        time_start = productivity.date_start.astimezone(local) if \
            productivity.date_start else False
        date_start_ms = time_start.timestamp() * 1000 if time_start else 0
        values["productivity"] = productivity

        return request.render("mes_web_controller.workorder_details", values)
