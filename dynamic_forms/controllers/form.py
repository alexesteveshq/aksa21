# -*- coding: utf-8 -*-

from odoo.addons.website.controllers.form import WebsiteForm
from odoo.http import request, route
import json


class DynamicForm(WebsiteForm):

    @staticmethod
    def get_report_data(kwargs, lead_id):
        lead = request.env['crm.lead'].browse(lead_id)
        excluded_fields = ['name', 'csrf_token']
        report_values = {}
        for key, value in kwargs.items():
            if key not in excluded_fields:
                if key in lead._fields:
                    field_name = lead._fields[key].string
                    report_values[field_name] = value if 'name' not in lead[key]._fields else lead[key].name
                else:
                    report_values[key] = value
        return report_values

    @route('/partner/info/<int:partner_id>', type='http', auth="public", methods=['GET'], website=True)
    def partner_info(self, partner_id, **kwargs):
        partner = request.env['res.partner'].browse(partner_id)
        return request.render('dynamic_forms.partner_info_template', {'partner': partner})

    @route('/website/form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def website_form(self, model_name, **kwargs):
        request.params = {key: value for key, value in request.params.items() if "#html_" not in key}
        res = super(DynamicForm, self).website_form(model_name, **kwargs)
        if model_name == 'crm.lead':
            data = json.loads(res.data.decode('utf-8'))
            report_values = self.get_report_data(kwargs, data['id'])
            content, type_report = request.env["ir.actions.report"]._render_qweb_pdf(
                'dynamic_forms.dynamic_form_report_view', [data['id']],
                data={'data': report_values})
            att = request.env['ir.attachment'].create({
                'name': 'Dynamic form report',
                'type': 'binary',
                'mimetype': 'application/pdf',
                'raw': content,
                'res_model': 'crm.lead',
                'res_id': data['id'],
            })
            res.data = json.dumps({'id': data['id'], 'report': att.id}).encode('utf-8')
        return res
