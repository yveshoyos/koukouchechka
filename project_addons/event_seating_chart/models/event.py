# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.http_routing.models.ir_http import slug, slugify
import json


class EventEvent(models.Model):
    _inherit = 'event.event'

    theater_id = fields.Many2one('event.theater', string='Theater')

    def open_website_set_seats_url(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/seating_chart/seat_seats/%s' % slug(self),
            'target': 'self',
        }


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    seat_ids = fields.Many2many('event.theater.seat', string='Seats')
    seats_count = fields.Integer(string='Number of seats', compute='_get_seats_count', store=True)

    @api.one
    @api.depends('seat_ids')
    def _get_seats_count(self):
        self.seats_count = len(self.seat_ids)
