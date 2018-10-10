# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.base.ir.ir_qweb.fields import nl2br


class WebsiteSeatingChart(http.Controller):
    @http.route('/event_seating/preview/<model("event.theater"):theater>', type='http', auth="user", website=True)
    def preview(self, theater, **kwargs):
        return request.render("event_seating.preview", {
            'theater': theater,
        })

    @http.route('/event_seating/seat_seats/<model("event.event"):event>', type='http', auth="user", website=True)
    def set_seats(self, event, **kwargs):
        return request.render("event_seating.seat_selection", {
            'event': event,
        })
