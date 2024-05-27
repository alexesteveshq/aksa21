# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'POS Order Delete',
    'summary': 'Deletes orders from point of sale. Point of sale order delete',
    'description': 'Deletes orders from point of sale. Point of sale order delete',
    'category': 'Point of sale',
    'author': 'Visionee',
    'version': '16.0.1.1',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'security/pos_order_delete_security.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
