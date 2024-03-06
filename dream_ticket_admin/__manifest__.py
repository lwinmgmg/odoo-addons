# pylint: disable=pointless-statement,missing-module-docstring
{
    "name": "Dream Ticket Management",
    "version": "1.0.0",
    "category": "Application",
    "summary": "Dream Ticket Management",
    "description": "Dream Ticket Management",
    "sequence": "1",
    "website": "https://www.cosmosmm.com",
    "author": "Lwin Maung Maung",
    "maintainer": "lwinmaungmaung@cosmosmm.com",
    "license": "LGPL-3",
    "support": "cosmossolutionservice@gmail.com",
    "depends": [
        "base",
        "api_user"
    ],
    "dependencies": [
        "pydantic>=2.6"
    ],
    "demo": [],
    "data": [
        "security/ir.model.access.csv",
        "security/ticket_user.xml",
        "views/ticket_view.xml",
        "wizards/ticket_wizard.xml",
        "wizards/ticket_line_wizard.xml",
        "views/menus.xml"
    ],
    "application": True,
    "installable": True,
}
