# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http, _
from odoo.http import request
import pytz


class Main(http.Controller):

    def wc_order(self, wc):
        """
        returns active workorders of a workcenter
        @param wc : workcenter
        """
        # _todo_ decidere come gestire il caso di gerarchia wc con presenza di parent_id
        # _???_ se c'è un parent_id non vengono caricati ordini sul wc?
        orders = request.env["mrp.workorder"].search(
            [
                ("workcenter_id", "=", wc.id),
                ("state", "not in", ["done", "cancel"]),
                ("production_state", "not in", ["draft", "done", "cancel"]),
            ],
            limit=200,
            order="date_planned_start",
            )
        return orders

    @http.route(
        [
            "/mes_wc_working/open_wos/<workcenter_id>",
            "/mes_wc_working/open_wos/",
        ],
        type="http",
        csrf=False,
        auth="user",
        website=True,
        )
    def workorders(self, workcenter_id=None, **post):
        """
        _todo_
        POST params
        @param view_wc : id of the workcenter to show
        @param view_wo : id of the workorder to show
        """

        # _todo_ cambiare nome variabile barcode
        user_tz = request.env.user.tz or str(pytz.utc.zone)
        local = pytz.timezone(user_tz)
        view_wc = post.get("view_wc", False)
        view_wo = post.get("view_wo", False)
        wc_id = False

        if view_wo:
            # redirect to wo details
            return http.local_redirect("/mes_wc_working/wo/%s" % view_wo)

        workcenter_id = int(workcenter_id) if workcenter_id else False

        try:
            wc_id = int(view_wc) if view_wc else workcenter_id
            wc = request.env["mrp.workcenter"].search([('id', '=', wc_id)])
            if not wc:
                # _todo_ sistemare messaggio
                raise Exception

            wos = self.wc_order(wc)

            values = {
                "wc": wc,
                "wos": wos,
                }
            # get last open productivity
            productivity = request.env["mrp.workcenter.productivity"].search(
                [("workcenter_id", "=", wc.id), ("date_end", "=", False)],
                order="date_start desc",
                limit=1,
                )
            # _todo_P_ gestire se ci sono più productivity
            if productivity.id:
                # show productivity data
                time_start = productivity.date_start.astimezone(local)
                date_start_ms = time_start.timestamp() * 1000

                if not productivity.loss_id.manual:
                    # if production isn't stopped (loss_id.manual=false) show wo details
                    values.update({
                        "productivity": productivity,
                        "workcenter": wc,
                        "wo": productivity.workorder_id,
                        "state": productivity.loss_id.loss_state,
                        "data_start_msec": date_start_ms,
                        "employee_ids": productivity.employee_ids,
                        })
                    return request.render(
                        "mes_web_controller.workorder_details",
                        values
                        )
                else:
                    # if production is stoped (loss_id.manual=true) show wo loss info
                    values = {
                        "productivity": productivity,
                        "workcenter": wc,
                        "wo": productivity.workorder_id,
                        "state": productivity.loss_id.loss_state,
                        "data_start_msec": date_start_ms,
                        "employee_ids": productivity.employee_ids,
                        }
                    return request.render(
                            "mes_web_controller.workorder_alert",
                            values
                            )
            else:
                # show wo of the wc
                return request.render(
                    "mes_web_controller.workorder_list",
                    values
                    )
        except Exception:
            # show wc list and wrong workcenter_id message
            wcs = request.env["mrp.workcenter"].search(
                [("count_open_wo", "!=", 0)],
                order="name",
                )
            values = {
                "wcs": wcs,
                "error": _("Error: Workcenter ID %s not found" % wc_id),
                }
            return request.render(
                "mes_web_controller.workcenter_working",
                values
                )
