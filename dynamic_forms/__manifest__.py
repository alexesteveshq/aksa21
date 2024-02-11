# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Dynamic Forms',
    'summary': 'Dynamic Forms',
    'description': 'Dynamic Forms',
    'category': 'Website',
    'author': 'Alex Esteves',
    'depends': [
        'website',
        'website_crm_partner_assign',
    ],
    'data': [
        'views/snippet.xml',
        'views/snippets/dynamic_form.xml',
        'views/dynamic_form_report_templates.xml',
        'views/dynamic_form_reports.xml',
    ],
    'assets': {
        'website.assets_wysiwyg': [
            'dynamic_forms/static/src/js/dynamic_form.js',
            'dynamic_forms/static/src/css/dynamic_form.css',
            'dynamic_forms/static/src/css/dynamic_form.scss',
            'dynamic_forms/static/src/xml/website_form_editor.xml',
        ],
        'website.assets_editor': [
            'dynamic_forms/static/src/js/website_crm_editor.js'
        ],
        'web_editor.assets_wysiwyg': [
            'dynamic_forms/static/src/js/editor/snippets.editor.js',
            'dynamic_forms/static/src/js/editor/snippets.options.js',
        ],
        'web.assets_frontend': [
            'dynamic_forms/static/src/js/dynamic_form_snippet.js',
            'dynamic_forms/static/src/css/dynamic_form.css',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
