# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Workcenter Productivity Employee",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Add relation toemployee that does the production",
    "description": "_todo_",
    "category": "Manufacture",
    "author": "Stefano Consolaro",
    "maintainers": [],
    "website": "",
    "depends": [
        # OCB
        "mrp",
        "hr",
        ],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_workcenter_views.xml",
        ],
    "application": False,
    "installable": True,
    "auto-install": False,
}
