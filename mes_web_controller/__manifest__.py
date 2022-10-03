# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mobile Working",
    "version": "14.0.17.0.0",
    "license": "AGPL-3",
    "summary": "Mobile Working",
    "description": "Mobile Working",
    "category": "Manufacturing",
    "development_status": "Beta",
    "author": "Stefano Consolaro",

    "depends": [
        # _todo_
        # ODOO
        "web",

        # OCA

        # CUSTOM
        "web_menu",
        "mes_workcenter_department",
        "mes_workcenter_load",
        ],
    "data": [
        "views/web_menu.xml",
        "views/workcenter_working.xml",
        "views/department_working.xml",
        "views/workorder_list.xml",
        "views/workorder_details.xml",
        "views/workorder_alert.xml",
        "views/employee_list.xml",
        ],
    "application": False,
    "installable": True,
    "auto_install": False,
    }
