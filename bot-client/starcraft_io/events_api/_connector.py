from asyncio import AbstractEventLoop, get_event_loop
from datetime import datetime
from enum import Enum, auto
from functools import partial
from typing import *

from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dataclasses_config import MainConfig, main_config, Duration, DynamicClass
from functional import Option, Some

from ..bank_api import Bank
from ._model import *
from ._events import *
from ._bank import *

@main_config
class ConnectorConfig(MainConfig):
    update_interval: Duration
    disconnect_timeout: Duration
    
    scheduler_class: DynamicClass[BaseScheduler]
    bank_class: DynamicClass[Bank]
    
    bank_name: str
    local_run: bool
    publisher_id: Optional[str] = None
    player_id: Optional[str] = None
    account_id: Optional[str] = None

class ConnectionState(Enum):
    Missing = auto()
    Connected = auto()
    NotConnected = auto()
    Disconnected = auto()

class StarCraftConnector:
    events_bank: EventsBank
    loop: AbstractEventLoop
    scheduler: BaseScheduler
    conf: ConnectorConfig
    
    connection_state: ConnectionState = ConnectionState.NotConnected
    last_ping_received: Option[datetime] = Option.empty
    
    def __init__(self, conf: ConnectorConfig):
        self.conf = conf
        self.scheduler = self.conf.scheduler_class.cls()
        self.init_bank()
    
    def init_bank(self):
        print(f"{datetime.now()}: Loading bank...")
        try:
            bank = self.conf.bank_class.cls.open \
            (
                bank_name = self.conf.bank_name,
                local_run = self.conf.local_run,
                publisher_id = self.conf.publisher_id,
                player_id = self.conf.player_id,
                account_id = self.conf.account_id,
            )
            self.events_bank = EventsBank(bank)
        except FileNotFoundError:
            self.connection_state = ConnectionState.Missing
        else:
            self.connection_state = ConnectionState.NotConnected
    
    def check_connection(self):
        print(f"{datetime.now()}: Connection state: {self.connection_state}")
        if (self.last_ping_received.map(lambda t: datetime.now() - t > self.conf.disconnect_timeout).get_or_else(False)):
            self.connection_state = self.connection_state.Disconnected
    
    def poll_responses(self):
        print(f"{datetime.now()}: Asking for updates...")
        self.events_bank.reload()
        
        event_ids = self.events_bank.event_ids(MessageType.Response, pop=True)
        for ev_id in event_ids:
            self.loop.call_soon_threadsafe(partial(self.handle_response, ev_id))
    
    def ping(self):
        print(f"{datetime.now()}: Making ping...")
        self.events_bank.add_event(PingEvent.new_request())
    
    def publish_requests(self):
        self.events_bank.save()
    
    def periodic(self):
        if (self.connection_state == ConnectionState.Missing):
            self.init_bank()
            return
        
        self.check_connection()
        self.poll_responses()
        self.ping()
        self.publish_requests()
    
    def handle_response(self, event_id: str):
        e = self.events_bank.pop_event(event_id, MessageType.Response)
        print(f"{datetime.now()}: {e} accepted")
        
        if (e.event_data.event_type == EventType.Ping):
            self.connection_state = ConnectionState.Connected
            self.last_ping_received = Some(datetime.now())
    
    # noinspection PyTypeChecker
    def start(self):
        self.loop = get_event_loop()
        self.scheduler.start()
        self.scheduler.add_job(self.periodic, trigger=IntervalTrigger(seconds=self.conf.update_interval.total_seconds()))
        self.loop.run_forever()

__all__ = \
[
    'ConnectorConfig',
    'StarCraftConnector',
]
