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

        user_tz = request.env.user.tz or str(pytz.utc.zone)
        local = pytz.timezone(user_tz)

        action = post.get("action", False)
        loss_id = post.get("loss_id", False)
        loss_id_set = post.get("loss_id_set", False)
        if loss_id_set:
            loss_id = int(loss_id_set)
        search_id = post.get("search_id", False)  # _!!!_ sostituire variabile
        search_name = post.get("search_name", '')
        wc_id = post.get("workcenter_id", False)

        wc = request.env["mrp.workcenter"].browse(int(wc_id))

        # _???_ verificare utilizzo
        if action == "wc_list":
            return http.local_redirect("/mes_wc_working/%s" % wc.department_id.id)
        # _???_ verificare utilizzo
        if action == "workcenter":
            return http.local_redirect("/mes_wc_working/open_wos/%s" % wc_id)

        if wc_id:
            wc = request.env["mrp.workcenter"].browse(int(wc_id))
        else:
            # _todo_ predisporre messaggio errore
            return http.local_redirect("/mes_wc_working")

        if action == "employees":
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

        if search_id:
            try:
                loss_id = int(search_id)
                loss = (
                    request.env["mrp.workcenter.productivity.loss"]
                    .browse(loss_id)
                    .exists()
                    )
                if not loss:
                    # _todo_ gestire messaggio eccezzione
                    raise Exception
            except Exception:
                loss_ids = request.env["mrp.workcenter.productivity.loss"].search(
                    [
                        ("loss_type", "=", "availability"),
                        # a standard i fermi sono ('manual', '=', 'true')
                    ],
                    limit=20,
                    order="name",
                    )
                values = {
                    "loss_ids": loss_ids,
                    "wc": wc,
                    "error": _("Loss id <b>%s</d> not found" % search_id),
                    }
                return request.render("mes_web_controller.workorder_alert", values)

        if search_name.strip() != '':
            try:
                loss_ids = (
                    request.env["mrp.workcenter.productivity.loss"]
                    .search([
                        ("name", 'ilike', search_name),
                        ("loss_type", "=", "availability"),
                        ])
                    )
                if not loss_ids:
                    raise Exception
            except Exception:
                loss_ids = request.env["mrp.workcenter.productivity.loss"].search(
                    [
                        ("loss_type", "=", "availability"),
                        # a standard i fermi sono ('manual', '=', 'true')
                    ],
                    limit=20,
                    order="name",
                    )
                values = {
                    "loss_ids": loss_ids,
                    "wc": wc,
                    "search_name": search_name,
                    "error": _("Loss with name like <b>%s</b> not found" % search_name),
                    }
                return request.render("mes_web_controller.workorder_alert", values)

            values = {
                "loss_ids": loss_ids,
                "wc": wc,
                "search_name": search_name,
                "error": '',
                }
            return request.render("mes_web_controller.workorder_alert", values)
        if loss_id:
            # record productivity loss
            # stop all wo _???_ verificare metodo
            wc.order_ids.end_all()
            employees = (
                request.env["mrp.workcenter.productivity"]
                .search(
                    [("workcenter_id", "=", wc.id)],
                    order="date_start desc",
                    limit=1
                )
                .employee_ids
                )
            if employees:
                employees.mapped("employee_id")
            productivity = request.env["mrp.workcenter.productivity"].create(
                {
                    "workcenter_id": wc.id,
                    "loss_id": loss_id,
                    "employee_ids": [(0, 0, {"employee_id": e}) for e in employees.ids],
                }
                )
            time_start = productivity.date_start.astimezone(local)
            date_start_ms = time_start.timestamp() * 1000  # value to pass to jquery
            values = {
                "productivity": productivity,
                "wc": productivity.workcenter_id,
                "data_start_msec": date_start_ms,
                "employee_ids": productivity.employee_ids,
                }
            return request.render("mes_web_controller.workorder_alert", values)
        else:
            # show wo list
            # activate wc _???_ verificare metodo
            wc.unblock()
            return http.local_redirect("/mes_wc_working/open_wos/" + str(wc_id))
