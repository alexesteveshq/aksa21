# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'POS discount calculator',
    'summary': 'POS discount calculator',
    'description': 'POS discount calculator',
    'category': 'Point of Sale',
    'author': 'Alex Esteves',
    'depends': [
        'pos_ext',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_discount_calc/static/src/**/*',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
