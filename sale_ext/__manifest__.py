# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Extend',
    'summary': 'Sale module extension',
    'description': 'Sale module extension',
    'category': 'Sale',
    'author': 'Alex Esteves',
    'depends': [
        'sale',
        'stock_ext',
    ],
    'data': [
        'views/sale_views.xml',
        'views/product_pricelist_views.xml',
        'views/sale_ext_templates.xml',
        'security/ir.model.access.csv',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
