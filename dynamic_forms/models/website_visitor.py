# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.http import request


class WebsiteVisitor(models.Model):
    _inherit = 'website.visitor'

    def _get_visitor_from_request(self, force_create=False, force_track_values=None):
        if request.session.no_auth:
            return self.env['website.visitor']
        return super(WebsiteVisitor, self)._get_visitor_from_request(force_create, force_track_values)
