# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name' : 'l10n_mx_partner_address',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/México',
    'description': """
This module adds the fields: 'l10n_mx_street3','l10n_mx_street4','l10n_mx_city2' used in México address. 
You can see this fields in partner form following the next steps:
    1.- The company's country needs to be México
    2.- The user must be assigned a company with country México defined

    This is very usable if you are working with multicompany schema.
    """,
    'website': 'http://mikrointeracciones.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'base',
        # 'l10n_mx_colonies',
        'l10n_mx_regimen_fiscal',
    ],
    # 'demo' : ['demo/l10n_mx_partner_address_demo.xml',],
    'data': [
        'views/country_data.xml',
        'views/res_company_view_inherit.xml',
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'active': False,
}
