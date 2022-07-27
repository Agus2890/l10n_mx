# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'l10n_mx_facturae_cer',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/México',
    'description': """
This module allows add certificates required for Factura-E MX
    """,
    'website': 'http://mikrointeracciones.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'l10n_mx_facturae_groups',
        # 'l10n_mx_company_multi_address',
        'l10n_mx_facturae_lib',
    ],
    'demo': [
        'demo/l10n_mx_facturae_cer_demo.xml'
    ],
    'data': [
        'security/l10n_mx_facturae_cer_security.xml',
        'security/ir.model.access.csv',
        'views/res_company_view.xml',
        # 'wizard/installer.xml',
    ],
    'installable': True,
    'active': False,
}
