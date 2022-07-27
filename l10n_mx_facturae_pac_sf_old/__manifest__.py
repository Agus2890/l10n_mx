# -*- encoding: utf-8 -*-
##############################################################################
#    Module Writen to Odoo, Open Source Management Solution
#
#    Copyright (c) 2008 MKI - http://www.mikrointeracciones.com.mx
#    All Rights Reserved.
#    info@mikrointeracciones.com.mx
##############################################################################
#    Coded by: Ricardo Gutiérrez (ricardo.gutierrez@mikrointeracciones.com.mx)
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': """
        Creacion de Factura Electronica para Mexico (CFDI-2011)
        - PAC Solucion Factible
    """,
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/México',
    'description': """
This module creates interface for
e-invoice files from invoices with Solucion Factible.
Ubuntu Package Depends:
    sudo apt-get install python-soappy "Not is requiered since Odoo v11"
""",
    'website': 'http://mikrointeracciones.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'l10n_mx_facturae_groups',
        'l10n_mx_params_pac',
        'l10n_mx_account_tax_category',
        'l10n_mx_ir_attachment_facturae',
        'l10n_mx_facturae_pac',
        'l10n_mx_facturae_group_show_wizards',
        'l10n_mx_payment_cfdi',        
        'account_cancel',
    ],
    'demo': [
        'demo/l10n_mx_facturae_pac_sf_demo.xml',
        'demo/l10n_mx_facturae_seq_demo.xml',
    ],
    'data': [],
    'installable': True,
    'active': False,
}
