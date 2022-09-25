# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http, _
from odoo.http import request
import pytz


class Main(http.Controller):
    @http.route(
        "/mes_wc_working/done/",
        type="http",
        csrf=False,
        auth="user",
        website=True
        )
    def workorder_done(self, **post):
        """
        _todo_
        @param productivity_id :
        @param action : back|employee|block|record_production|record_setup
        @param pcs_ok :
        @param pcs_ko :
        """
        user_tz = request.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        productivity_id = post.get("productivity_id", False)

        if post.get("action", False) == "wc_list":
            return http.local_redirect("/mes_wc_working")

        if post.get("action", False) == "workcenter":
            return http.local_redirect(
                "/mes_wc_working/open_wos/%s" % post.get("wc_id", False)
                )

        # check if productivity exsists
        try:
            productivity = request.env["mrp.workcenter.productivity"].browse(
                int(productivity_id)
            )
        except request.exceptions:
            # _todo_ verificare se except request.exceptions va bene
            return http.local_redirect("/mobile_mrp_working")

        wo = productivity.workorder_id
        wc_id = wo.workcenter_id.id
        wc = request.env["mrp.workcenter"].browse(int(wc_id))

        if post.get("action", False) == "employees":
            # open employee view
            values = {
                "title": "Employees",
                "productivity_id": productivity_id,
                "employees": productivity.employee_ids,
            }
            return request.render("mes_web_controller.employee_list", values)

        if post.get("action", False) == "block":
            # open loss view
            alerts = request.env["mrp.workcenter.productivity.loss"].search(
                [
                    ("loss_type", "=", "availability")
                    # a standard i fermi sono ('manual', '=', 'true')
                ],
                limit=20,
                order="name",
                )
            values = {
                "title": "Mobile Alert",
                "alerts": alerts,
                "workcenter": wc,
                "employee_ids": productivity.employee_ids,
                }
            return request.render("mes_web_controller.workorder_alert", values)

        if post.get("action", False) == "record_production":
            # records production
            if not productivity.employee_ids:
                # goes back to wo if no employee declared
                time_start = productivity.date_start.astimezone(local)
                date_start_ms = time_start.timestamp() * 1000  # value to pass to jquery
                values = {
                    "error": _("At least one employee must be specified"),
                    "productivity": productivity,
                    "workcenter": wc,
                    "wo": productivity.workorder_id,
                    "data_start_msec": date_start_ms,
                    }
                return request.render("mes_web_controller.workorder_details", values)

            # _todo_P_ aggiungere scarti? -> inserire campo su mrp.productivity e
            # modificare funzione end_previous
            # _todo_P_ aggiungere il campo su qt productivity? Il campo produced su wo
            # sarebbe meglio computed rispetto productivity
            # _todo_P_ prevedere come aggiornare qt su parametro su funzione
            # endprevious(doall=True)

            # update pcs of productivity
            pcs_ok = post.get("pcs_ok", 0)
            pcs_ko = post.get("pcs_ko", 0)
            if not pcs_ok or pcs_ok == "":
                pcs_ok = 0
            if not pcs_ko or pcs_ko == "":
                pcs_ko = 0
            productivity.write(
                {
                    "qty_produced": float(pcs_ok),
                    "qty_scrap": float(pcs_ko),
                }
            )
            # update wo status
            wo.qty_produced += float(pcs_ok)
            if wo.qty_produced >= wo.qty_production:
                wo.button_finish()
            else:
                wo.end_previous()
            # show wo list
            return http.local_redirect("/mobile_mrp_working/open_wos/" + str(wc_id))

        if post.get("action", False) == "record_setup":
            if not productivity.employee_ids:
                # goes back to wo if no employee declared
                time_start = productivity.date_start.astimezone(local)
                date_start_ms = time_start.timestamp() * 1000  # value to pass to jquery
                values = {
                    "error": _("At least one employee must be specified"),
                    "productivity": productivity,
                    "workcenter": wc,
                    "wo": productivity.workorder_id,
                    "data_start_msec": date_start_ms,
                    }
                # show wo details
                return request.render("mes_web_controller.workorder_details", values)

            # _???_ che fa?
            wo.end_previous()
            # _todo_P_ implementare oggetto productivity con cambio causale
            # show wo list
            return http.local_redirect("/mobile_mrp_working/open_wos/" + str(wc_id))
