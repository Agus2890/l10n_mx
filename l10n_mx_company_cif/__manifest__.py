# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'l10n_mx_company_cif',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/México',
    'description' : """
This module add image field to company for CIF (RFC)
    """,
    'website': 'www.mikrointeracciones.com.mx',
    'license': 'AGPL-3',
    'depends' : [
        'account',
        'base',
    ],
    'demo' : [],
    'data' : [
        'views/res_company_view.xml',
        'wizard/installer.xml',
    ],
    'installable' : True,
    'active' : False,
}
