# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
#from odoo import fields, orm
from odoo.tools.translate import _


class ProductImportInfo(models.Model):
    # ===========================================================================
    # product_import_info
    #
    # This object holds the information that determine the quantity of products
    # are expected per Import Document
    # ===========================================================================
    _name = 'product.import.info'
    _rec_name = 'import_id'

    # @api.v7
    # def _get_qtymoved(self, cr, uid, ids, field_name, arg, context=None):
    # # TODO ISAAC: Metodo para calcular la cantidad de movimientos ya imputados a este import info.
    # # Analizar desde cero, no contemplar lo que este escrito aqui.
    # # Recordar quitar los TODO.
    #     '''
    #     cr.execute("""
    #         SELECT stock_move.id, stock_move.product_qty, stock_picking.type,
    #             stock_move.*
    #         FROM stock_move
    #         INNER JOIN stock_tracking
    #            ON stock_tracking.id = stock_move.tracking_id
    #         INNER JOIN import_info
    #            ON import_info.id = stock_tracking.import_id
    #         LEFT OUTER JOIN stock_picking
    #           ON stock_picking.id = stock_move.picking_id
    #         WHERE stock_picking.type = 'in'
    #           --AND stock_move.state = 'done'
    #     """)
    #     '''
    #     result = {}
    #     for i in ids:
    #         result[i] = 10.00

    #     return result

    product_id = fields.Many2one(
        'product.product', strin='Product', required=True,
            domain=[
                '|', ('type', '=', 'consu'), ('type', '=', 'product'),
                '&', ('pack_control', '=', True), ('purchase_ok', '=', True)
            ],
            help="Product to be counted on this Import Document information"
        )
    import_id = fields.Many2one(
            'import.info', string='Import Info', required=True,
            help="Import Document related"
        )
    qty = fields.Float(
            string='Quantity', digits=(16, 4),
            help="Quantity of this product on this document,"
        )
    uom_id = fields.Many2one(
            'product.uom', string='UoM', required=False,
            help='Unit of measure, be care this unit must be on the same '
                 'category of unit indicated on the product form.'
        )
    # qty_moved = fields.Float(
    #         string='Qty already moved', compute='_get_qtymoved', method=True,   
    #     )

    # @api.v7
    # def _check_uom(self, cr, uid, ids, context=None):
    #     for import_info in self.browse(cr, uid, ids, context=context):
    #         if (
    #             import_info.uom_id and import_info.uom_id.category_id.id !=
    #             import_info.product_id.uom_po_id.category_id.id
    #         ):
    #             return False
    #     return True

    # _constraints = [
    #     (_check_uom, _('Error: The default UOM and the Import '
    #                    'Product Info must be in the same category.'),
    #      ['uom_id'])
    # ]

    # _sql_constraints = [
    #     ('product_import_uniq', 'unique (product_id,import_id)',
    #      'Product must appear only once per Import Document !')
    # ]

    # @api.v7
    # def onchange_product_id(self, cr, uid, ids, product_id, context=None):
    #     """
    #     Return a dict that contains new values, and context

    #     @param cr: cursor to database
    #     @param user: id of current user
    #     @param product_id: latest value from user input for field product_id
    #     @param args: other arguments
    #     @param context: context arguments, like lang, time zone

    #     @return: return a dict that contains new values, and context
    #     """
    #     res = {}
    #     if product_id:
    #         product_obj = self.pool.get('product.product')
    #         product = product_obj.browse(cr, uid, product_id, context)
    #         res = {'value': {'uom_id': product.uom_po_id.id}}
    #     return res


class ProductTemplate(models.Model):
    """
    product_product
    """
    _inherit = 'product.template'


    # def _has_import(self, cr, uid, ids, field_name, arg, context=None):
    #     result = {}
    #     for i in ids:
    #         if len(self.browse(cr, uid, [i], context)[0].import_info_ids) != 0:
    #             result[i] = True
    #         else:
    #             result[i] = False
    #     return result

    #@api.multi
    # def _has_import(self):
    #     result = {}
    #     for i in ids:
    #         if len(self.browse(cr, uid, [i], context)[0].import_info_ids) != 0:
    #             result[i] = True
    #         else:
    #             result[i] = False
    #     return result

    pack_control = fields.Boolean(
            string='Enable Import Control', required=False,
            help='If you want to track import information to be used on '
                 'invoices and other documents check this field, remember, '
                 'if the product is a service this information can not '
                 'be tracked, if this field is checked you will need to '
                 'use consumable or stockable type of product on '
                 'information page.'
        )
    import_info_ids = fields.One2many(
            'product.import.info', 'product_id',
            'Import Info', required=False
        )
    has_import = fields.Boolean(
            string='Has Import'
            #compute='_has_import', method=True, string='Has Import'
        )

    # TODO: Add validation to ensure no services products are used with pack_control
