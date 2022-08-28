# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import _OrderedDictKeysView
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
        # se c'è un parent_id non vengono caricati ordini sul wc?
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
        @param btn : exit
        @param barcode : id of the workcenter
        @workcenter_id : id of the workcenter
        """
        user_tz = request.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        btn = post.get("btn", False)
        barcode = post.get("barcode", False)
        workcenter_id = False

        if False and btn == "exit":
            # go back to main menu
            return http.local_redirect("/mobile")
        if barcode:
            workcenter_id = barcode
        try:
            wc_id = int(workcenter_id)
            wc = request.env["mrp.workcenter"].browse(wc_id)
            if not wc.active:
                # _todo_ sistemare messaggio
                raise Exception

            wos = self.wc_order(wc)

            values = {
                "title": "Workorder of the Workcenter",
                "wc": wc,
                "wos": wos,
                }
            # get open productivity
            productivity = request.env["mrp.workcenter.productivity"].search(
                [("workcenter_id", "=", wc.id), ("date_end", "=", False)],
                order="date_start desc",
                limit=1,
                )
            # _todo_ gestire se ci sono più productivity
            if productivity.id:
                # show productivity data
                time_start = productivity.date_start.astimezone(local)
                date_start_ms = time_start.timestamp() * 1000  # value to pass to jquery

                if not productivity.loss_id.manual:  # oppure action = block _???_
                    # _???_ show wo details
                    values.update(
                        {
                            "title": "Workorder of the Workcenter",
                            "productivity": productivity,
                            "workcenter": wc,
                            "wo": productivity.workorder_id,
                            "action": productivity.action,
                            "data_start_msec": date_start_ms,
                        }
                    )
                    return request.render("mes_web_controller.workorder_details", values)
                else:
                    # _???_ show productivity loss
                    values = {
                        "productivity": productivity,
                        "workcenter": wc,
                        "data_start_msec": date_start_ms,
                        "employee_ids": productivity.employee_ids,
                    }
                    return request.render("mes_web_controller.alert_list", values)
            else:
                # show wo of the wc
                return request.render("mes_web_controller.workorder_list", values)
        except:
            # _todo_ capire che variabile passare ad exception (flake8)
            # pop wrong barcode message and show wc list
            wcs = request.env["mrp.workcenter"].search([])
            values = {
                "title": "Workorder of the Workcenter",
                "wcs": wcs,
                "error": _("Error: barcode not found"),
            }
            return request.render("mes_web_controller.workcenter_list", values)
