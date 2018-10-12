var chart, last_selected, selected_seats = [], seat_num = 1;
var $counter, $cart, $grouped;

function group_seats(seats) {
    if (jQuery.isEmptyObject(seats)) {
        return [];
    }
    var number_label = {};
    var numbers = [];
    for (var id in seats) {
        var label = seats[id];
        var num = parseInt(label.replace(/\D/g, ""), 10);
        number_label[num] = label;
        numbers.push(num);
    }
    numbers = numbers.sort(function (a, b) { return a - b; });
    var groups = [[number_label[numbers[0]]]];
    var n = 0;
    for (var i=1; i < numbers.length; i++) {
        if (numbers[i-1] + 1 == numbers[i]) {
            groups[n].push(number_label[numbers[i]]);
        }
        else {
            n++;
            groups[n] = [number_label[numbers[i]]];
        }
    }
    return groups;
}

function html_group_seats(seats) {
    var groups = group_seats(seats);
    var res = [];
    var n = 0;
    for (var i in groups) {
        if (groups[i].length > 1) {
            var first = groups[i][0];
            var last = groups[i].slice(-1)[0];
            res.push(first + ' - ' + last);
        }
        else if (groups[i].length == 1) {
            res.push(groups[i][0]);
        }
    }
    return res.join('<br/>');
}

function select_seat(seat) {
    selected_seats[seat.settings.id] = seat.settings.label;
    $('<span class="label label-primary"/>').text(seat.settings.label)
        .attr('id', 'cart-item-' + seat.settings.id)
        .data('seat-id', seat.settings.id)
        .appendTo($cart);
    $cart.append(' ');
}

function unselect_seat(seat) {
    delete selected_seats[seat.settings.id];
    $('#cart-item-' + seat.settings.id).remove();
}

function select_multiple(seat, last_selected_seat, target) {
    var from = $('.seatCharts-seat').index(seat.node());
    var to = $('.seatCharts-seat').index(last_selected_seat.node());
    var start = Math.min(from, to) + 1;
    var end = Math.max(from, to);
    $('.seatCharts-seat').slice(start, end).each(function () {
        var seat = chart.get($(this).attr('id'));
        if (seat.status() != 'unavailable') {
            seat.status(target);
            if (target == 'selected') {
                select_seat(seat);
            }
            else {
                unselect_seat(seat);
            }
        }
    });
}

function load_seating_chart(counter_selector, cart_selector, group_selector) {
    if (counter_selector) {
        $counter = $(counter_selector);
        $cart = $(cart_selector);
        $grouped = $(group_selector);
    }
    var config = {
        map: map,
        seats: seats,
        legend: {
            node: $('#legend'),
            items: legend
        },
        naming: {
            top: false,
            left: true,
            rows: rows,
            getId: function(character, row, column) {
                return row + '-' + seat_num;
            },
            getLabel: function (character, row, column) {
                return row + '-' + seat_num++;
            }
        }
    };
    if (counter_selector) {
        config.click = function (e) {
            if (last_selected && e && e.shiftKey) {
                var target = this.status() == 'selected' ? 'available' : 'selected';
                select_multiple(this, last_selected, target);
            }
            last_selected = this;
            if (this.status() == 'available') {
                select_seat(this);
                $counter.text(selected_seats.length);
                $grouped.html(html_group_seats(selected_seats));
                return 'selected';
            }
            else if (this.status() == 'selected') {
                unselect_seat(this);
                $counter.text(selected_seats.length);
                $grouped.html(html_group_seats(selected_seats));
                return 'available';
            }
            else if (this.status() == 'unavailable') {
                return 'unavailable';
            }
            return this.style();
        };
    }
    chart = $('#seat-map').seatCharts(config);
    if (counter_selector) {
        $('.unselect_all_seats').on('click', function () {
            chart.find('selected').node().click();
        });
    }
}