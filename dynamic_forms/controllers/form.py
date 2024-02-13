# -*- coding: utf-8 -*-

from odoo.addons.website.controllers.form import WebsiteForm
from odoo.http import request, route
import json


class DynamicForm(WebsiteForm):

    @staticmethod
    def get_report_data(kwargs, lead_id):
        lead = request.env['crm.lead'].browse(lead_id)
        excluded_fields = ['name', 'csrf_token', 'expected_revenue']
        report_values = {}
        for key, value in kwargs.items():
            if key not in excluded_fields:
                if key in lead._fields:
                    if hasattr(lead[key], 'name'):
                        report_values[key] = lead[key].name
                    else:
                        report_values[key] = value
                elif 'state_partner_id' in key:
                    report_values[key.replace('state_partner_id', '')] = lead['state_partner_id'].name
                elif 'partner_assigned_id' in key:
                    report_values[key.replace('partner_assigned_id', '')] = lead['partner_assigned_id'].name
                else:
                    report_values[key] = value
        lead.dynamic_form_data = json.dumps(report_values)

    @route('/website/form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def website_form(self, model_name, **kwargs):
        request.params = {key: value for key, value in request.params.items() if "#html_" not in key}
        new_params = {}
        for key, param in request.params.items():
            if 'state_partner_id' in key:
                new_params['state_partner_id'] = param
            elif 'partner_assigned_id' in key:
                new_params['partner_assigned_id'] = param
            else:
                new_params[key] = param
        request.params = new_params
        res = super(DynamicForm, self).website_form(model_name, **kwargs)
        if model_name == 'crm.lead':
            data = json.loads(res.data.decode('utf-8'))
            self.get_report_data(kwargs, data['id'])
            res.data = json.dumps({'id': data['id'],
                                   'report': "/report/pdf/dynamic_forms.dynamic_form_report_view/%s" % data['id']}
                                  ).encode('utf-8')
        return res
