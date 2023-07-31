# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime


import dateutil.parser
import pytz
import pprint
from odoo.tools import consteq, float_round, image_process, ustr
from werkzeug import urls

from odoo import api, fields, models, _
# from odoo.addons.payment.models.payment_acquirer import ValidationError

# from odoo.tools.float_utils import float_compare
# from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.waafipay.controllers.controllers import Waafipay
# from odoo.addons.payment_gateway.wipay_payment.controllers.controllers import WipayController
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import dateutil, pytz
from werkzeug import urls
_logger = logging.getLogger(__name__)


class PaymentTransactionInherit(models.Model):
    _inherit = 'payment.transaction'

    def render_sale_button(self, order, submit_txt=None, render_values=None):
        values = {
            'partner_id': order.partner_id.id,
            'type': self.type,
            'wafi_payment_type': self.env.context.get("wafi_payment_type")
        }
        if render_values:
            values.update(render_values)
        # Not very elegant to do that here but no choice regarding the design.
        self._log_payment_transaction_sent()
        return self.acquirer_id.with_context(submit_class='btn btn-primary', submit_txt=submit_txt or _('Pay Now')).sudo().render(
            self.reference,
            order.amount_total,
            order.pricelist_id.currency_id.id,
            values=values,
        )


class WaafiPay(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[
        ('waafipay', 'waafipay')
    ], ondelete={'waafipay': 'set default'})
    waafipay_merchant_id = fields.Char(string="Merchant ID", required=True)
    waafipay_storekey = fields.Char(string="Store key", required=True)
    waafipay_storeid = fields.Char(string="Store ID", required=True)
    bank = fields.Boolean(string="Bank Account")
    creditcard = fields.Boolean(string="Credit Card")
    mobilwallet = fields.Boolean(string="Mobile Account")

    @api.model
    def _get_waafipay_urls(self, environment):

        """ waafipay URLS """
        if environment == 'prod':
            return {
                'waafipay_form_url': 'https://api.waafipay.net/asm',
            }
        else:
            return {
                'waafipay_form_url': 'https://sandbox.waafipay.net/asm',
            }

    def waafipay_form_generate_values(self, values):
        base_url = self.get_base_url()
        if values['wafi_payment_type'] == 'bank':
            payment_type = 'MWALLET_BANKACCOUNT'
        elif values['wafi_payment_type'] == 'credit':
            payment_type = 'CREDIT_CARD'
        elif values['wafi_payment_type'] == 'mobile':
            payment_type = 'MWALLET_ACCOUNT'


        import requests
        url = "https://sandbox.safarifoneict.com/asm"

        payload = "{\n                \"schemaVersion\"    : \"1.0\"," \
                  "\n                \"requestId\"         : \"R17100517154423\"," \
                  "\n                \"timestamp\"         : \"%s\"," \
                  "\n                \"channelName\"       : \"WEB\"," \
                  "\n                \"serviceName\"       : \"HPP_PURCHASE\"," \
                  "\n                \"serviceParams\": {" \
                  "\n                        \"storeId\"               : \"%s\"," \
                  "\n                        \"hppKey\"                : \"%s\"," \
                  "\n                        \"merchantUid\"           : \"%s\"," \
                  "\n                        \"hppSuccessCallbackUrl\" : \"%s\"," \
                  "\n                        \"hppFailureCallbackUrl\" : \"%s\"," \
                  "\n                        \"hppRespDataFormat\"  : \"4\"," \
                  "\n                        \"paymentMethod\"    : \"%s\"," \
                  "\n                        \n \"transactionInfo\" : {" \
                  "\n                                \"referenceId\"   : \"'%s'\"," \
                  "\n                                \"invoiceId\"  : \"'%s'\"," \
                  "\n                                \"amount\"     : \"%s\"," \
                  "\n                                \"currency\"   : \"%s\"," \
                  "\n                                \"description\": \"testing\"\n}\n}\n}" % (datetime.now(), self.waafipay_storeid, self.waafipay_storekey, self.waafipay_merchant_id,urls.url_join(base_url, Waafipay._return_url),urls.url_join(base_url, Waafipay._return_url), payment_type, values['reference'].replace("-","/"),values['reference'].replace("-","/"), values["amount"], values["currency"].name )
        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache",
        }

        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)

        hppUrl = response.json()['params']["hppUrl"]
        hppRequestId = response.json()['params']["hppRequestId"]
        referenceId = response.json()['params']["referenceId"]
        waafipay_tx_values = dict(values)
        waafipay_tx_values.update({
            "hppUrl": hppUrl,
            "hppRequestId": hppRequestId,
            "referenceId": referenceId,
        })
        return waafipay_tx_values

    def waafipay_get_form_action_url(self):
        self.ensure_one()
        environment = 'prod' if self.state == 'enabled' else 'test'
        return self._get_waafipay_urls(environment)['waafipay_form_url']


class WaafipayPayment(models.Model):           #form transaction
    _inherit = 'payment.transaction'

    # waafipay_hash = fields.Char('Hash')

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    @api.model
    def _waafipay_form_get_tx_from_data(self, data):
        reference = data.json()['params']['referenceId'].split("'")[1].replace("/","-")
        if not reference:
            error_msg = _('waafipay: received data with missing reference (%s) or txn_id (%s)') % (reference, txn_id)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'waafipay: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    def _waafipay_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        # # TODO: txn_id: shoudl be false at draft, set afterwards, and verified with txn details

        return invalid_parameters

    def _waafipay_form_validate(self, data):
        status = data.json()['params']['state']
        former_tx_state = self.state
        res = {
            'acquirer_reference': data.json()['params']['referenceId'].split("'")[1].replace("/","-"),
        }

        if status in ['APPROVED']:
            try:
                # dateutil and pytz don't recognize abbreviations PDT/PST
                tzinfos = {
                    'PST': -8 * 3600,
                    'PDT': -7 * 3600,
                }
                date = dateutil.parser.parse(data.get('date'), tzinfos=tzinfos).astimezone(pytz.utc).replace(
                    tzinfo=None)
            except:
                date = fields.Datetime.now()
            res.update(date=date)
            self._set_transaction_done()
            if self.state == 'done' and self.state != former_tx_state:
                _logger.info('Validated waafipay payment for tx %s: set as done' % (self.reference))
                return self.write(res)
            return True
        else:
            error = 'Received unrecognized status for waafipay payment %s: %s, set as error' % (self.reference, status)
            res.update(state_message=error)
            self._set_transaction_cancel()
            if self.state == 'cancel' and self.state != former_tx_state:
                _logger.info(error)
                return self.write(res)
            return True
