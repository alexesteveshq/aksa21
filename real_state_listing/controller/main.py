# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from werkzeug.exceptions import NotFound

from odoo.http import Controller, request, route, content_disposition


class RealState(Controller):

    @route(['/real_state/list_properties'], type='json', auth="public", cors='*', methods=['POST'])
    def list_properties(self, **kwargs):
        properties = request.env['real.state.property'].sudo().search([])
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        properties = [{'id': prop.id,'name': prop.name, 'description': prop.description, 'status': prop.state,
                       'url': '' if not prop.image.image_src else base_url + prop.image.image_src, 'price': prop.price}
                      for prop in properties]
        return properties

    @route('/web/image/<string:xmlid>/<string:filename>', type='http', auth="public", cors='*')
    def image(self, xmlid=None, filename=None, **kwargs):
        attachment = request.env.ref(xmlid)
        if attachment:
            content = attachment.datas
            response = request.make_response(content, content_type=attachment.mimetype)
            return response
        return request.not_found()