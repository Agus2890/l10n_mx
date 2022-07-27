# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo.tools.translate import _
import logging
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)

class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    import_id = fields.Many2one(
            'import.info', 'Import Lot', required=False,
            help='Import Information, it is required for manipulation if '
                 'import info needed in invoices.'
        )


class StockQuant(models.Model):
    _inherit = "stock.quant"

    import_id = fields.Many2one(
            'import.info', 'Import Lot', compute='get_import_id', readonly=True,
            help='Import Information, it is required for manipulation if '
                 'import info needed in invoices.'
        )

    @api.one
    def get_import_id(self):
        if self.lot_id:
            self.import_id = self.lot_id.import_id

class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    import_id = fields.Many2one(
            'import.info', 'Import Lot', compute='get_import_id', readonly=True,
            help='Import Information, it is required for manipulation if '
                 'import info needed in invoices.'
        )

    @api.one
    def get_import_id(self):
        if self.prod_lot_id:
            self.import_id = self.prod_lot_id.import_id

    # @api.one
    # def _get_prodlot_change(self, cr, uid, ids, context=None):
    #     return self.pool.get('stock.inventory.line').search(cr, uid, [('prod_lot_id', 'in', ids)], context=context)


    # @api.model
    # def get_import_id(self):
    #     if self.line_ids.prod_lot_id:
    #         self.line_ids.import_id = self.line_ids.prod_lot_id.import_id  

# class StockInventory(models.Model):
#     _inherit = "stock.inventory"


# class stock_tracking(orm.Model):
#     _inherit = "stock.tracking"
#     _columns = {
#         'import_id': fields.many2one(
#             'import.info', 'Import Lot', required=False,
#             help='Import Information, it is required for manipulation if '
#                  'import info needed in invoices.'
#         )
#     }

#     def name_get(self, cr, uid, ids, context=None):
#         ids = isinstance(ids, (int, long)) and [ids] or ids
#         if not len(ids):
#             return []
#         # Avoiding use 000 in show name.
#         res = [(r['id'], ''.join([a for a in r['name'] if a != '0']) + '::' + (
#             self.browse(cr, uid, r['id'], context).import_id.name or '')) \
#             for r in self.read(cr, uid, ids, ['name', ], context)]
#         return res


# class stock_move_constraint(orm.Model):
#     """
#     stock_move for validations in the move of inventory
#     """
#     _inherit = 'stock.move'

#     def _check_product_qty(self, cr, uid, ids, context=None):
#         """Check if quantity of product planified on import info document is
#         bigger than this qty plus qty already received with this tracking lot
#         """

#         product_import_info_obj = self.pool.get('product.import.info')
#         uom_obj = self.pool.get('product.uom')
#         for move in self.browse(cr, uid, ids, context=context):

#             import_id = (move.tracking_id and move.tracking_id.import_id and
#                          move.tracking_id.import_id.id or False)

#             if import_id:
#                 product_import_info_ids = product_import_info_obj.search(
#                     cr, uid,
#                     [('import_id', '=', import_id),
#                      ('product_id', '=', move.product_id.id)
#                      ],
#                     context=context
#                 )
#                 for product_import_info in product_import_info_obj.browse(
#                     cr, uid, product_import_info_ids, context=context
#                 ):
#                     # Qty moved on this stock move
#                     qty_dflt_stock = uom_obj._compute_qty(
#                         cr, uid,
#                         move.product_uom.id, move.product_qty,
#                         move.product_id.uom_id.id
#                     )
#                     # Qty assigned on this Import Document
#                     qty_dflt_import = uom_obj._compute_qty(
#                         cr, uid,
#                         product_import_info.uom_id.id, product_import_info.qty,
#                         product_import_info.product_id.uom_id.id
#                     )
#                     # Qty already moved on other stock moves related to
#                     # this Import Document
#                     qty_moved = product_import_info.qty_moved
#                     # Total qty
#                     remain = qty_dflt_import - qty_moved
#                     if qty_dflt_stock > remain:
#                         _logger.debug('cantidad mayor %s > %s' % (qty_dflt_stock, remain))
#                         return False

#         return True

#     def _check_if_product_in_track(self, cr, uid, ids, context=None):
#         """
#         Check if product at least exist in import track

#         Validar, que si tiene pack_control, valide que tenga el
#         informacion de importacion y que ademas exista el producto en
#         este import_info
#         Si no tiene pack_control, y ademas le agregaste import_info,
#         obligalo a que quite el import_info ya que no es necesario.
#         Si no tiene pack_control y no tiene import_info, dejalo pasar
#         """
#         for move in self.browse(cr, uid, ids, context=context):
#             # purchase o sale, generate a stock.move with state confirmed or
#             # draft, then not validate with these states.
#             if move.state != 'done':
#                 return True
#             import_info = move.tracking_id and move.tracking_id.import_id or False
#             if move.product_id.pack_control:
#                 if not import_info:
#                     return False

#                 for product in import_info.product_info_ids:
#                     # Optimizando perfomance: En cuanto lo encuentre en la
#                     # iteracion, se detenga y lo retorne y ya no siga buscando
#                     if move.product_id.id == product.product_id.id:
#                         return True

#             else:
#                 # Not a controlled product
#                 return True
#         return False

#     def onchange_track_id(self, cr, user, track_id, context=None):
#         """
#         Return a dict that contains new values, and context
#         @param cr: cursor to database
#         @param user: id of current user
#         @param track_id: latest value from user input for field track_id
#         @param context: context arguments, like lang, time zone
#         @return: return a dict that contains new values, and context
#         """
#         if context is None:
#             context = {}
#         return {
#             'value': {},
#             'context': {},
#         }

#     def _check_import_info(self, cr, uid, ids, context=None):
#         """ Checks track lot with import information is assigned to stock move or not.
#         @return: True or False
#         """
#         for move in self.browse(cr, uid, ids, context=context):
#             # Check if i need to verify the track for import info.
#             if not move.tracking_id and (move.state == 'done' and(
#                 (move.product_id.pack_control and move.location_id.usage == 'production') or
#                 (move.product_id.pack_control and move.location_id.usage == 'internal') or
#                 (move.product_id.pack_control and move.location_id.usage == 'inventory') or
#                 (move.product_id.pack_control and move.location_dest_id.usage == 'production') or
#                 (move.product_id.pack_control and move.location_id.usage == 'supplier') or
#                 (move.product_id.pack_control and move.location_dest_id.usage == 'customer')
#             )):
#                 return False

#         return True

#     _constraints = [
#         (_check_import_info,
#          _('You must assign a Pack for this stock move'),
#          ['tracking_id']),
#         (_check_if_product_in_track,
#          _('The selected Pack does not have an Import Control Document '
#            'associated.'),
#          ['tracking_id']),
#         # TODO: Correct this
#         # (_check_product_qty,
#         # _('Product quantity in selected Pack is bigger than product '
#         #   'quantity on related Import Info Document.'),
#         # ['tracking_id'])
#     ]


# class stock_picking(orm.Model):
#     _inherit = "stock.picking"

#     def _prepare_invoice_line(
#         self, cr, uid, group, picking, move_line, invoice_id,
#         invoice_vals, context=None
#     ):
#         if context is None:
#             context = {}
#         invoice_line_data = super(stock_picking, self)._prepare_invoice_line(
#             cr, uid, group, picking, move_line, invoice_id,
#             invoice_vals, context=context
#         )
#         invoice_line_data.update({
#             'move_id': move_line.id,
#             'tracking_id': move_line.tracking_id and move_line.tracking_id.id
#         })
#         return invoice_line_data
