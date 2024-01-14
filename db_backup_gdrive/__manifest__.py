# pylint: disable=pointless-statement,missing-module-docstring
{
    'name': 'Backup Database to Google Drive',
    'version': '1.0.0',
    'category': 'Tools',
    'summary': 'Backup Database to Google Drive',
    'description': 'Backup Database to Google Drive',
    'sequence': '1',
    'website': 'https://www.cosmos.com',
    'author': 'Lwin Maung Maung',
    'maintainer': 'Cosmos',
    'license': 'LGPL-3',
    'support': 'cosmossolutionservice@gmail.com',
    'depends': [
        'base',
    ],
    'dependencies':[
        "google-api-python-client==2.113.0",
        "google-auth-httplib2==0.2.0",
        "google-auth-oauthlib==1.2.0"
    ],
    'demo': [],
    'data': [
        "views/gdrive_settings.xml",
        "views/menus.xml",
        "security/ir.model.access.csv",
        "data/backup_n_delete_crons.xml"
    ],
    'application': True,
    'installable': True
}
