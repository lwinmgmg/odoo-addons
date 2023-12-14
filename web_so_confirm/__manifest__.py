{
    'name': 'Website Sale Order Confirm',
    'version': '1.0.0',
    'category': 'Website',
    'summary': 'Order confirm website sale',
    'description': 'Order confirm website sale',
    'sequence': '1',
    'website': 'https://www.thedreamtickets.com',
    'author': 'Lwin Maung Maung',
    'maintainer': 'The Dream Tickes',
    'license': 'LGPL-3',
    'support': 'odoomates@gmail.com',
    'depends': [
        'base', 'sale', 'website_sale'
    ],
    'demo': [],
    'data': [
        'views/sale_order_view.xml'
    ],
    'application': True,
    'installable': True
}