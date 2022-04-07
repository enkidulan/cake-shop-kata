__version__ = "0.1.0"


from dataclasses import dataclass, field
import datetime
import arrow


@dataclass
class CakeOrder:
    cake_size: str = None
    order_time: datetime.datetime = None
    frosting: bool = None
    fancy_box: bool = None
    with_nuts: bool = None
    delivery_date: datetime.date = None
    worklog: list = field(default_factory=list)


def get_next_time(day, off_days=frozenset()):
    day = day.shift(days=1)
    while day.weekday() in off_days:
        day = day.shift(days=1)
    return day


def calculate_delivery_date(cake_order):
    lead_time = 2 if cake_order.cake_size == "small" else 3
    last_action_time = cake_order.order_time
    if cake_order.order_time.hour < 12:
        last_action_time = cake_order.order_time.shift(days=-1)

    # xmas
    if (
        last_action_time.month == 12
        and (last_action_time.day + (3 if cake_order.fancy_box else lead_time)) > 22
    ):
        last_action_time = arrow.get(year=last_action_time.year + 1, month=1, day=1)

    for _ in range(lead_time):
        last_action_time = get_next_time(last_action_time, off_days={5, 6})
        cake_order.worklog.append(["Marco", "bakes", str(last_action_time)])
    if cake_order.frosting:
        for _ in range(2):
            last_action_time = get_next_time(last_action_time, off_days={6, 0})
            cake_order.worklog.append(["Sandro", "frosts", str(last_action_time)])
    if cake_order.with_nuts:
        last_action_time = get_next_time(last_action_time, off_days={5, 6})
        cake_order.worklog.append(["Marco", "adds nuts", str(last_action_time)])

    if cake_order.fancy_box:
        # this should go last
        while (last_action_time - cake_order.order_time).days < 2:
            last_action_time = get_next_time(last_action_time)
            cake_order.worklog.append(["waiting for fancy box", str(last_action_time)])
        cake_order.worklog.append(
            ["box arrives", str(cake_order.order_time.shift(days=2))]
        )
    return last_action_time


def place_cake_order(**query):
    order = CakeOrder(**query)
    return order
