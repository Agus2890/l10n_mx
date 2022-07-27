# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo import SUPERUSER_ID
from lxml import etree
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_mx_street3 = fields.Char('No. External', size=128, help='External number of the partner address')
    l10n_mx_street4 = fields.Char('No. Internal', size=128, help='Internal number of the partner address')
    l10n_mx_city2 = fields.Char('Locality', size=128, help='Locality for this partner')
    country_id = fields.Many2one('res.country', string='Country', default=lambda self: self._get_default_country_id(), ondelete='restrict')

    def _address_fields(self):
        _("Returns the list of the address fields that synchronizes from the "
          "parent when the flag is set use_parent_address.")
        res = super(ResPartner, self)._address_fields()
        res.extend(['l10n_mx_street3', 'l10n_mx_street4', 'l10n_mx_city2'])
        return res

    def _get_default_country_id(self):
        country_obj = self.env['res.country']
        ids = country_obj.search([('code', '=', 'MX'), ], limit=1)
        rid = ids and ids.id or False
        return rid

    # def _fields_view_get_address(self, arch):
    #     locality = _('Locality...')
    #     street = _('Street...')
    #     street2 = _('Colony...')             
    #     cp = _('ZIP')
    #     state = _('State')
    #     external = _('No External...')
    #     internal = _('No Internal...')
    #     country = _('Country...')
    #     city2 = _('City...')
    #     res = super(ResPartner, self)._fields_view_get_address(arch)
    #     user_obj = self.env['res.users']
    #     fmt = user_obj.browse(self.env.user.id).company_id.country_id
    #     fmt = fmt and fmt.address_format
    #     city = '<field name="city" placeholder="%s" style="width: 40%%"/>' % (city2)
    #     for name, field in self:#._fields.iteritems():
    #         if name == 'city_id':
    #             city = '<field name="city" modifiers="{&quot;invisible&quot;: true}" placeholder= "%s" style="width: 50%%"/><field name="city_id" on_change="1" placeholder="%s" style="width: 40%%"/>' % (city2, city2)    
    #     layouts = {
    #         '%(street)s %(l10n_mx_street3)s %(l10n_mx_street4)s\n%(street2)s %(city)s %(l10n_mx_city2)s\n%(state_name)s %(country_name)s %(zip)s':
    #             """
    #             <group>
    #                 <group>
    #                     <field name="type" attrs="{'invisible': [('parent_id','=', False)]}" groups="base.group_no_one"/>
    #                     <label for="street" string="Address"/>
    #                     <div class="o_address_format">
    #                         <div attrs="{'invisible': ['|', ('parent_id', '=', False), ('type', '!=', 'contact')]}" class="oe_edit_only"><b>Company Address:</b></div>

    #                         <field name="street" placeholder="%s" class="o_address_street" 
    #                             attrs="{'readonly': [('type', '=', 'contact'),('parent_id', '!=', False)]}"/>
    #                         <field name="l10n_mx_street3" placeholder="%s"/>
    #                         <field name="l10n_mx_street4" placeholder="%s"/>
    #                         <field name="street2" placeholder="%s" class="o_address_street" 
    #                             attrs="{'readonly': [('type', '=', 'contact'),('parent_id', '!=', False)]}"/>
    #                         <div class="o_address_format">
    #                             %s
    #                             <field name="state_id" class="o_address_state" placeholder="%s" options='{"no_open": True}'
    #                                 attrs="{'readonly': [('type', '=', 'contact'),('parent_id', '!=', False)]}" 
    #                                 context="{'country_id': country_id, 'zip': zip}" style="width: 37%%"/>
    #                             <field name="zip" placeholder="%s" class="o_address_zip"
    #                                 attrs="{'readonly': [('type', '=', 'contact'),('parent_id', '!=', False)]}"
    #                                 style="width: 20%%"/>       
    #                         </div>
    #                         <field name="l10n_mx_city2" placeholder="%s"/>
    #                         <field name="country_id" placeholder="%s" 
    #                             class="o_address_country" 
    #                             options="{&quot;no_open&quot;: True, &quot;no_create&quot;: True}" 
    #                             attrs="{'readonly': [('type', '=', 'contact'),('parent_id', '!=', False)]}"/>
    #                     </div>
    #                     <field name="vat" placeholder="e.g. BE0477472701" 
    #                         attrs="{'readonly': [('parent_id','!=',False)]}"/>       
    #                 </group>
    #                 <group>
    #                     <field name="function" 
    #                         placeholder="e.g. Sales Director" 
    #                         attrs="{'invisible': [('is_company','=', True)]}"/>
    #                     <field name="phone" widget="phone"/>
    #                     <field name="mobile" widget="phone"/>
    #                     <field name="user_ids" invisible="1"/>
    #                     <field name="email" widget="email" context="{'gravatar_image': True}" 
    #                         attrs="{'required': [('user_ids','!=', [])]}"/>
    #                     <field name="website" widget="url" 
    #                         placeholder="e.g. https://www.odoo.com"/>
    #                     <field name="title"
    #                         options="{&quot;no_open&quot;: True}" 
    #                         attrs="{'invisible': [('is_company', '=', True)]}"/>
    #                     <field name="lang"/>
    #                     <field name="category_id"
    #                         widget="many2many_tags" options="{'color_field': 'color', 'no_create_edit': True}" 
    #                         placeholder="Tags..."/>  
    #                 </group>
    #             </group>
    #             """ %
    #             (street, external, internal, street2, city, state, cp,
    #              locality, country)
    #     }

    #     for k, v in layouts.items():
    #         doc = etree.fromstring(res)
    #         for node in doc.xpath("//form/sheet/group"):
    #             tree = etree.fromstring(v)
    #             node.getparent().replace(node, tree)
    #         arch = etree.tostring(doc)
    #         arch or res
    #     return arch

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        if (not view_id) and (view_type == 'form') and self._context.get('force_email'):
            view_id = self.env.ref('base.view_partner_simple_form').id
        res = super(ResPartner, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            fields_get = self.fields_get(
                ['l10n_mx_street3', 'l10n_mx_street4', 'l10n_mx_city2'],
            )
            res['fields'].update(fields_get)
        return res
