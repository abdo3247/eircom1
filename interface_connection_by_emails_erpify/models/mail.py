# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError, Warning
from odoo.tools.safe_eval import safe_eval
import datetime
import logging
import dateutil

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_route(self, message, message_dict, model=None, thread_id=None, custom_values=None):
        email_to = message_dict['to']
        email_to_localpart = (tools.email_split(email_to) or [''])[0].split('@', 1)[0].lower()
        matches = self.env['email.interfaces.erpify'].search([('state', '=', 'active'), ('alias_name', '=', email_to_localpart)])
        _logger.info('Finding a match for '+email_to_localpart)
        if matches:
            _logger.info('Match Found.')
            msg = self.env['mail.thread'].message_new(message_dict)
            new_records = matches.get_and_store_decoded_data(msg.attachment_ids)
            matches.message_post(subject=message.subject, body='File received and processed. ' + str(new_records) + ' new records are created.', attachments=message.attachment_ids)
        else:
            _logger.info('Match not Found.')
            super(MailThread, self).message_route(message, message_dict, model=model, thread_id=thread_id, custom_values=custom_values)
