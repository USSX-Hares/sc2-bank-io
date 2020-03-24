from dataclasses import dataclass, InitVar, field
from datetime import datetime
from typing import *

from functional.option import *

from ._model import *

DateTimeAllowedTypes = [ datetime, float, int ]
DateTimeMergedType = Union[datetime, float, int, Option[Union[datetime, float, int]], None]

@dataclass
class PingEvent(Event):
    @property
    def timestamp(self) -> Option[datetime]:
        if (self.event_data.custom_data):
            return Some(self.event_data.custom_data).map(float).map(datetime.fromtimestamp)
        else:
            return Option.empty
    
    @timestamp.setter
    def timestamp(self, v: DateTimeMergedType):
        if (not isinstance(v, Option)):
            v = Option(v)
        
        self.event_data.custom_data = v \
            .map(lambda x: str(int(x.timestamp() if (isinstance(x, datetime)) else x))) \
            .get_or_else('') \
    
    _associated_event_type = EventType.Ping
    @classmethod
    def _new(cls, timestamp: DateTimeMergedType = None, **kwargs) -> 'PingEvent':
        result: PingEvent = super()._new(**kwargs)
        result.timestamp = timestamp or datetime.now()
        return result

@dataclass
class DisconnectionEvent(Event):
    @property
    def reason(self) -> str:
        return self.event_data.custom_data
    @reason.setter
    def reason(self, value: str):
        self.event_data.custom_data = value
    
    _associated_event_type = EventType.Disconnection
    @classmethod
    def _new(cls, reason: str, **kwargs) -> 'DisconnectionEvent':
        result: DisconnectionEvent = super()._new(**kwargs)
        result.reason = reason
        return result

@dataclass
class AllocateUnitEvent(Event):
    @property
    def filter(self) -> str:
        if (self.message_type == MessageType.Request):
            return self.event_data.custom_data
        else:
            raise ValueError(f"Order field is available only for requests")
    @filter.setter
    def filter(self, value: str):
        if (self.message_type == MessageType.Request):
            self.event_data.custom_data = value
        else:
            raise ValueError(f"Order field is available only for requests")
    
    _associated_event_type = EventType.AllocateUnit
    @classmethod
    def new_request(cls, filter: str = None, **kwargs) -> 'AllocateUnitEvent':
        result: AllocateUnitEvent = super()._new(**kwargs)
        if (filter):
            result.filter = filter
        return result

@dataclass
class IssueOrderEvent(Event):
    @property
    def order(self) -> str:
        if (self.message_type == MessageType.Request):
            return self.event_data.custom_data
        else:
            raise ValueError(f"Order field is available only for requests")
    @order.setter
    def order(self, value: str):
        if (self.message_type == MessageType.Request):
            self.event_data.custom_data = value
        else:
            raise ValueError(f"Order field is available only for requests")
    
    _associated_event_type = EventType.IssueOrder
    @classmethod
    def new_request(cls, order: str = None, **kwargs) -> 'IssueOrderEvent':
        result: IssueOrderEvent = super()._new(**kwargs)
        if (order):
            result.order = order
        return result

@dataclass
class RevokeOwnerEvent(Event):
    _associated_event_type = EventType.RevokeOwner
@dataclass
class UnitDiesEvent(Event):
    _associated_event_type = EventType.UnitDies


EVENT_MAPPING: Dict[EventType, Type[Event]] = \
{
    EventType.Ping: PingEvent,
    EventType.Disconnection: DisconnectionEvent,
    EventType.AllocateUnit: AllocateUnitEvent,
    EventType.IssueOrder: IssueOrderEvent,
    EventType.RevokeOwner: RevokeOwnerEvent,
    EventType.UnitDies: UnitDiesEvent,
}

__all__ = \
[
    'AllocateUnitEvent',
    'DisconnectionEvent',
    'IssueOrderEvent',
    'PingEvent',
    'RevokeOwnerEvent',
    'UnitDiesEvent',
    
    'EVENT_MAPPING',
]
