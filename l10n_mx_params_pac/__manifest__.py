# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Reading dynamic parameters to be sent to PAC for Mexico Electronic Invoice (CFDI-2011) ',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/México',
    'description' : """
This module reads the params required for PAC.
    """,
    'website': 'www.mikrointeracciones.com.mx',
    'license': 'AGPL-3',
    'depends' : ['base',
                'l10n_mx_facturae_groups'],
    'demo' : [],
    'data' : [
        'security/ir.model.access.csv',
        'views/params_pac_view.xml',
        'security/params_pac_security.xml'
    ],
    'installable' : True,
    'active' : False,
}
