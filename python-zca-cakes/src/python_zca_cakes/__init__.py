__version__ = "0.1.0"


from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from dateutil.tz import tzutc
from zope import component
from zope.interface import Interface
from zope.interface.interfaces import IComponentLookup
from zope.interface.registry import Components

WEEK_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class IAction(Interface):
    pass


class ICakeShop(Interface):
    pass


class IWorkersRegistry(Interface):
    pass


class IBakingPlanner(Interface):
    """Person that takes part in cakes creation."""


@dataclass
class CakeOrder:
    cake_size: str = None
    order_time: datetime = None
    last_update_time: datetime = None
    add_frosting: bool = None
    add_fancy_box: bool = None
    add_nuts: bool = None
    delivery_date: date = None
    baking_schedule: list = field(default_factory=list)


@dataclass
class Action:
    name: str = None
    lead_time: int = None


@dataclass
class BusinessPartner:
    name: str = None
    skills: set = field(default_factory=set)
    work_days: set = field(default_factory=set)


@dataclass
class CakeShop:
    def __init__(self):
        gsm = component.getSiteManager()
        self.sitemanager = Components(bases=[gsm])

    def __conform__(self, interface):
        if interface.isOrExtends(IComponentLookup):
            return self.sitemanager


class WorkersRegistry:

    def get_worker(self, skill, time_point):
        for worker in self._wokers:
            if skill not in worker.skills:
                continue
            if WEEK_DAYS[time_point.weekday()] in worker.work_days:
                return worker


def _create_baking_schedule(shop, cake_order, time_point=None):


    def schedule_action(action_name, time_point):
        workers_registry = component.getUtility(IWorkersRegistry, context=shop)
        action = component.getUtility(IAction, action_name, context=shop)

        for _ in range(action.lead_time):
            for attempt in range(10):
                time_point = time_point + timedelta(days=1)
                worker = workers_registry.get_worker(action_name, time_point)
                if worker:
                    cake_order.baking_schedule.append([worker.name, action.name, time_point.strftime("%Y-%m-%d")])
                    break
            else:
                raise RuntimeError(f"Can't find worker after {attempt} attempts")

        return time_point

    def schedule_async_action(action_name, time_point, base_time):
        action = component.getUtility(IAction, action_name, context=shop)
        remaining_lead_time = action.lead_time - (time_point - base_time).days - 1
        time_point = time_point + timedelta(days=remaining_lead_time)
        cake_order.baking_schedule.append([action.name, time_point.strftime("%Y-%m-%d")])
        return time_point

    if time_point is None:
        time_point = cake_order.order_time
        if cake_order.order_time.hour < 12:
            # work starts on the same day if oder received in the morning
            time_point = time_point - timedelta(days=1)

    if cake_order.add_fancy_box:
        time_point = schedule_action("order_box", time_point)
    cake_type = "bake_small_cake" if cake_order.cake_size == "small" else "bake_large_cake"
    time_point = schedule_action(cake_type, time_point)
    if cake_order.add_frosting:
        time_point = schedule_action("add_frosting", time_point)
    if cake_order.add_nuts:
        time_point = schedule_action("add_nuts", time_point)
    if cake_order.add_fancy_box:
        box_arrived = schedule_async_action("wait_for_box", time_point, cake_order.order_time)
        if box_arrived > time_point:
            time_point = box_arrived

    # xmas
    if time_point.month == 12 and time_point.day > 22:
        cake_order.baking_schedule = []
        time_point = datetime(year=time_point.year + 1, month=1, day=1, tzinfo=tzutc())
        return _create_baking_schedule(shop, cake_order, time_point=time_point)

    cake_order.delivery_date = time_point
    return cake_order.delivery_date


# public high-level API


def calculate_delivery_date(cake_order, shop_name=""):
    cake_shop = component.getUtility(ICakeShop, name=shop_name)
    create_baking_schedule = component.getUtility(IBakingPlanner, context=cake_shop)
    create_baking_schedule(cake_shop, cake_order)
    return cake_order.delivery_date


def place_cake_order(**query):
    order = CakeOrder(**query)
    return order


def bootstrap_cake_shop():
    gsm = component.getSiteManager()

    cake_shop = CakeShop()
    gsm.registerUtility(cake_shop, ICakeShop)
    cake_shop_sm = component.getSiteManager(context=cake_shop)
    cake_shop_sm.registerUtility(_create_baking_schedule, IBakingPlanner)

    workers_registry = WorkersRegistry()
    workers_registry._wokers = [
        BusinessPartner(
            name="Marco",
            skills={
                "add_nuts",
                "bake_large_cake",
                "bake_small_cake",
                "order_box",
                "wait_for_box",
            },
            work_days=["Mon", "Tue", "Wed", "Thu", "Fri"],
        ),
        BusinessPartner(
            name="Sandro",
            skills={
                "add_frosting",
                "order_box",
                "wait_for_box",
            },
            work_days=["Tue", "Wed", "Thu", "Fri", "Sat"],
        ),
    ]
    cake_shop_sm.registerUtility(workers_registry, IWorkersRegistry)

    cake_shop_sm.registerUtility(Action("bakes", 3), IAction, "bake_large_cake")
    cake_shop_sm.registerUtility(Action("bakes", 2), IAction, "bake_small_cake")
    cake_shop_sm.registerUtility(Action("adds nuts", 1), IAction, "add_nuts")
    cake_shop_sm.registerUtility(Action("frosts", 2), IAction, "add_frosting")
    cake_shop_sm.registerUtility(Action("order_box", 0), IAction, "order_box")
    cake_shop_sm.registerUtility(Action("box arrives", 3), IAction, "wait_for_box")
