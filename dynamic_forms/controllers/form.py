# -*- coding: utf-8 -*-

from odoo.addons.website.controllers.form import WebsiteForm
from odoo.http import request, route
import json


class DynamicForm(WebsiteForm):

    def get_report_data(self, kwargs, lead):
        excluded_fields = ['name', 'csrf_token', 'expected_revenue']
        report_values = {}
        for key, value in kwargs.items():
            if key not in excluded_fields:
                field = self.find_lead_field(key)
                if field and hasattr(lead[field], 'name'):
                    report_values[key.replace(field, '')] = lead[field].name
                elif field:
                    report_values[key.replace(field, '')] = value
                else:
                    report_values[key] = value
        lead.dynamic_form_data = json.dumps(report_values)

    @staticmethod
    def find_lead_field(key):
        fields = request.env['crm.lead']._fields
        for field in fields:
            if key.startswith(field):
                return field
        return False

    @route('/website/form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def website_form(self, model_name, **kwargs):
        request.params = {key: value for key, value in request.params.items()
                          if "#html_" not in key and key not in ["expected_revenue"]}
        new_params = {}
        for key, param in request.params.items():
            field = self.find_lead_field(key) or key
            new_params[field] = param
        request.params = new_params
        res = super(DynamicForm, self).website_form(model_name, **kwargs)
        if model_name == 'crm.lead':
            data = json.loads(res.data.decode('utf-8'))
            lead = request.env['crm.lead'].sudo().browse(data['id'])
            lead.expected_revenue = float(kwargs.get('expected_revenue', 0))
            self.get_report_data(kwargs, lead)
            res.data = json.dumps({'id': data['id'],
                                   'report': "/report/pdf/dynamic_forms.dynamic_form_report_view/%s" % data['id']}
                                  ).encode('utf-8')
        return res
