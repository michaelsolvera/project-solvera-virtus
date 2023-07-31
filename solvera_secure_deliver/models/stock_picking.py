
import datetime
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero

class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def delivery(self):
        for i in self.move_ids_without_package:
            if self.picking_type_code == "outgoing":
                print("hea_kok_isa",i.quantity_done,i.reserved_availability)
                if i.quantity_done > i.reserved_availability:
                    raise UserError(('Harap Periksa quantity DONE yang di isi'))

        res =  super(StockPicking, self).delivery()
        return res