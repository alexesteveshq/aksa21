# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'POS Sellers',
    'summary': 'Point of sale seller features',
    'description': 'Point of sale seller features',
    'category': 'Point of Sale',
    'author': 'Alex Esteves',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_sellers/static/src/**/*',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}