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


class EventTheater(models.Model):
    _name = 'event.theater'
    _description = 'Theater'

    name = fields.Char(string='Name', required=True)
    disposition = fields.Text(string='Disposition', required=True)
    seats_names = fields.Text(string='Seats names', required=True)
    rows = fields.Selection([('letter', 'Letters'), ('number', 'Numbers')], string="Label on letters", default='letter', required=True)
    active = fields.Boolean(string='Active', default=True)

    @api.multi
    def open_website_url(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/seating_chart/preview/%s' % slug(self),
            'target': 'self',
        }

    @api.multi
    def get_json_disposition(self):
        self.ensure_one()
        res = []
        for row in self.disposition.strip().split('\n'):
            res.append(row.strip())
        return json.dumps(res)

    @api.multi
    def get_json_seats(self):
        self.ensure_one()
        res = {}
        for seat_name in self.seats_names.split('\n'):
            seat, name = seat_name.split(':', 1)
            seat = seat.strip()
            name = name.strip()
            res[seat] = {
                'classes': slugify(name),
                'category': name,
            }
        return json.dumps(res)

    @api.multi
    def get_json_legend_items(self):
        self.ensure_one()
        res = []
        for seat_name in self.seats_names.split('\n'):
            seat, name = seat_name.split(':', 1)
            seat = seat.strip()
            name = name.strip()
            res.append([seat, "available", name])
            res.append([seat, "unavailable", "Booked"])
        return json.dumps(res)

    @api.multi
    def get_rows(self):
        self.ensure_one()
        rows = self.disposition.strip().split('\n')
        res = range(1, len(rows) + 1, 1)
        if self.rows == 'letter':
            res = [chr(i + 64) for i in res]
        return json.dumps(res)

