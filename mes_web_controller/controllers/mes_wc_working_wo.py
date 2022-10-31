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
        * list management *
        @param dep_id : id of the department
        @param wc_id : id of the workcenter
        @param search_wo : id of the wo to search
        @param search_wide : string to use to search wos
        * wo management *
        @param action : block|search
        @param view_wo : id of the wo to view details
        @param start_wo : id of the wo to start
        @param setup_wo : id of the wo to setup
        """

        user_tz = request.env.user.tz or str(pytz.utc.zone)
        local = pytz.timezone(user_tz)

        action = post.get("action", False)
        dep_id = request.session.get('dep_id')
        dep_id = dep_id if dep_id else post.get("dep_id", False)
        wc_id = int(post.get("wc_id", False))
        view_wo = post.get("view_wo", False)
        start_wo = post.get("start_wo", False)
        setup_wo = post.get("setup_wo", False)
        search_wo = post.get("search_wo", '')
        search_wide = post.get("search_wide", '')

        wc = request.env["mrp.workcenter"].browse(wc_id)
        productivity = request.env["mrp.workcenter.productivity"]
        wo_id = False
        values = {}
        date_start_ms = ''

        # list update on empty search
        if action == 'search' and search_wo.strip() == '' and search_wide.strip() == '':
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
                    }
            return request.render("mes_web_controller.workorder_list", values)

        # check search value
        if search_wo:
            try:
                search_wo = int(search_wo)
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
                        "search_wide": search_wide,
                        "search_wo": search_wo,
                        "error": _(
                            "Error: work order ID <b>%s</b> is not numeric" %
                            search_wo),
                        }
                return request.render("mes_web_controller.workorder_list", values)

        if view_wo:
            workorder_id = int(view_wo)

        '''
        _!!!_ eliminare
        if action == "back" \
           and (not search_wo or search_wo == '') \
           and (not search_wide or search_wide == ''):
            # goes to main view
            return http.local_redirect("/mes_wc_working/%s" % wc.department_id.id)
        '''

        if workorder_id:
            # check wo id and get related wc
            try:
                wo_id = int(workorder_id)
                wc = request.env["mrp.workorder"].browse(wo_id).workcenter_id
                wc_id = wc.id
            # manage empty result
            except Exception:
                # request come from a department view
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
                            "Error: work order ID <b>%d</b> not found" %
                            int(workorder_id)),
                        }
                    return request.render(
                        "mes_web_controller.department_working", values
                        )
                # request come from all department list _???_
                else:
                    wcs = request.env["mrp.workcenter"].search(
                        [("count_open_wo", "!=", 0)],
                        order="name",
                        )
                    values = {
                        "wcs": wcs,
                        "error": _(
                            "Error: work order ID <b>%d</b> not found" %
                            int(workorder_id)),
                        }
                    return request.render(
                        "mes_web_controller.workcenter_working", values
                        )

        # manage options selected
        if start_wo:
            # set wo working status
            workorder_id = start_wo
            values = {
                "loss_state_id": "working",
                }
        elif setup_wo:
            # set wo setup status
            workorder_id = setup_wo
            values = {
                "loss_state_id": "preparation",
                }
        elif action == "block":
            # stop wo production
            loss_ids = request.env["mrp.workcenter.productivity.loss"].search(
                [("loss_type", "=", "availability")],
                limit=20,
                order="name",
                )
            values = {
                "loss_ids": loss_ids,
                "wc": wc,
                "loss_state_id": "stopped",
                # "employee_ids": False _todo_P_ passare gli employee del productivity
                # precedente?
                }
            # _todo_ sostituire workorder_alert con workcenter_alert per chiarezza
            return request.render("mes_web_controller.workorder_alert", values)
        elif (action == 'search'                            # click button search
              '''
              _!!!_ eliminare
              or (action == "back"                          # form post
                  and ((search_wide and search_wide != '')  # with a wide search
                       or (search_wo and search_wo != '')   # with an id search
                       )
                  )
              '''
              ) and not view_wo:
            # try to find wo based on search string
            # set base domain filter
            domain = [
                ("workcenter_id", "=", wc_id),
                ("state", "not in", ["done", "cancel"]),
                ]
            error = ''
            if search_wide:
                # search in wo details
                wos = self.wo_wide_search(
                        ['product', 'po'],
                        search_wide,
                        domain
                        )
                if not wos:
                    error = _("Info: No one work order with reference to <b>%s</b>"
                              % search_wide)
            else:
                # search specific wo
                workorder_id = int(search_wo)
                domain.append(('id', '=', workorder_id))
                wos = request.env["mrp.workorder"].search(
                    domain,
                    limit=200,
                    order="date_planned_start",
                )
                if not wos:
                    error = _(
                        "Error: work order ID <b>%s</b> not found in this workcenter"
                        % search_wo)
            if search_wo and not wos or search_wide:
                # show result list
                values.update({
                        "wc": wc,
                        "wos": wos,
                        "search_wide": search_wide,
                        "search_wo": search_wo,
                        "error": error,
                        })
                return request.render("mes_web_controller.workorder_list", values)
        elif not workorder_id:
            # goes to wo list of the wc
            return http.local_redirect(("/mes_wc_working/open_wos/%d" % wc_id))

        # extract wo based on wo_id selected
        try:
            wo = request.env["mrp.workorder"].search([
                ('workcenter_id', '=', wc_id),
                ('id', '=', workorder_id)
                ])
            if not wo.state or wo.state in ["done", "cancel"]:
                raise Exception
        except Exception:
            # _???_ gestione errore su id wo assente, duplicata da ottimizzare
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
                "search_wide": search_wide,
                "search_wo": search_wo,
                "error": _("Error: work order ID <b>%d</b> not found in this workcenter"
                           % workorder_id),
                }
            return request.render("mes_web_controller.workorder_list", values)

        # a wo has be found
        values["wo"] = wo
        values["workcenter"] = wo.workcenter_id

        # retrieves employees of last productivity
        # _???_ uses last employee productivity
        employees = (
            request.env["mrp.workcenter.productivity"].search(
                [("workcenter_id", "=", wc.id)],
                order="date_start desc",
                limit=1,
                ).employee_ids
            )

        if workorder_id:
            # get the last productivity info to show
            productivity = request.env["mrp.workcenter.productivity"].search(
                [
                    ("workcenter_id", "=", wo.workcenter_id.id),
                    ("workorder_id", "=", workorder_id),
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
                    ("workorder_id", "=", workorder_id),
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
