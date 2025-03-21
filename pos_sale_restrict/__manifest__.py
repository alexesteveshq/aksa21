{
    'name': 'POS sale restrict',
    'summary': 'POS sale restrict',
    'description': 'POS sale restrict',
    'category': 'Point of Sale',
    'author': 'Alex Esteves',
    'version': '1.0',
    'depends': [
        'point_of_sale', 'stock_ext'
    ],
    'data': [
        'views/pos_payment_method_views.xml',
        'views/res_config_settings_views.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_sale_restrict/static/src/**/*',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
}
