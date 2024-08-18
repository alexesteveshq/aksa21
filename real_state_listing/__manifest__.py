# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Real state listing',
    'summary': 'Real state module for listing properties',
    'description': 'Real state module for listing properties',
    'category': 'Real State',
    'author': 'Alex Esteves',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/real_state_property_views.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
