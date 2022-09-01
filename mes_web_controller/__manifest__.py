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
        "web_mobile_menu",
        ],
    "data": [
        "views/web_menu.xml",
        # "views/alert_list_view.xml",
        # "views/employee_list_view.xml",
        "views/workcenter_working_view.xml",
        # "views/workorder_details_view.xml",
        "views/workorder_list_view.xml",
        ],
    "application": False,
    "installable": True,
    "auto_install": False,
    }
