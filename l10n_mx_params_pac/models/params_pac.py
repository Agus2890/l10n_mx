# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ParamsPac(models.Model):
    _name = 'params.pac'

    @api.model
    def _get_method_type_selection(self):
        # From module of PAC inherit this function and add new methods
        types = []
        return types

    name = fields.Char('Name', size=128, required=True,
            help='Name for this param')
    url_webservice = fields.Char('URL WebService', size=256, required=True,
            help='URL of WebService used for send to sign the XML to PAC')
    namespace = fields.Char('NameSpace', size=256,
            help='NameSpace of XML of the page of WebService of the PAC')
    user = fields.Char('User', size=128, help='Name user for login to PAC')
    password = fields.Char('Password', size=128,
            help='Password user for login to PAC')
    method_type = fields.Selection(_get_method_type_selection,
            "Type of method",size=64, required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
            default=lambda s: s.env['res.company']._company_default_get('params.pac'),
            help='Company where will configurate this param')
    active = fields.Boolean('Active', default=1, help='Indicate if this param is active')
    sequence = fields.Integer('Sequence', default=10,
            help='If have more of a param, take the param with less sequence')
    certificate_link = fields.Char('Certificate link', size=256 ,
            help='PAC have a public certificate that is necessary by customers to check the validity of the XML and PDF')
        # 'link_type': fields.selection([('production','Produccion'),('test','Pruebas')],"Tipo de ligas"),
