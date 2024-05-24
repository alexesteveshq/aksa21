# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'POS Product cost',
    'summary': 'Adds product cost in point of sale order and lines.'
               'POS product cost|Point of sale product cost|Sold products cost|Sold product cost|'
               'POS cost|Point of sale cost',
    'description': 'Adds product cost in point of sale order and lines',
    'category': 'Point of sale',
    'author': 'Visionee',
    'version': '16.0.1.0',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'views/pos_order_views.xml',
        'views/pos_order_report_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
