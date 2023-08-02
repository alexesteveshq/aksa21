# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'POS Extend',
    'summary': 'Point of sale module extension',
    'description': 'Point of sale module extension',
    'category': 'Point of Sale',
    'author': 'Alex Esteves',
    'depends': [
        'point_of_sale',
        'stock_ext',
    ],
    'data': [
        'views/product_views.xml',
        'views/pos_order_report_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_ext/static/src/**/*',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
