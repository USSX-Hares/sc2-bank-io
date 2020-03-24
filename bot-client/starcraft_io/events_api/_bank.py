from dataclasses import dataclass, field
from types import MappingProxyType
from typing import *

from ..bank_api import Bank, AbstractBank
from ..util import MappingProxy
from ._model import *
from ._events import *

@dataclass
class EventsBank(AbstractBank):
    bank: Bank = field(repr=False)
    meta: MetaData = field(init=False)
    
    @property
    def events(self) -> Iterable[Event]:
        return self._events.values()
    @property
    def requests(self) -> MappingProxy[str, Event]:
        return self._proxies[MessageType.Request]
    @property
    def responses(self) -> MappingProxy[str, Event]:
        return self._proxies[MessageType.Response]
    
    def __post_init__(self):
        self._events = dict()
        self._proxies = dict()
        
        for message_type in MessageType: # type: MessageType
            self._proxies[message_type] = self._get_proxy(message_type)
        
        self.reload()
    
    def _get_proxy(self, message_type: MessageType) -> MappingProxy[str, Event]:
        return MappingProxy(lambda ev_id: self._events[message_type, ev_id], lambda: (e.event_id for e in self._events.values() if e.message_type == message_type))
    def _check_meta(self):
        if (self.meta.protocol_version != protocol_version):
            raise ValueError(f"Unsupported protocol version: {self.meta.protocol_version}, expected: {protocol_version}")
    
    def add_event(self, event: Event):
        raise NotImplementedError
    
    def reload(self):
        self.bank.reload()
        self.meta = MetaData.from_dict(self.bank['meta'].as_dict())
        self._check_meta()
        
        for message_type in MessageType: # type: MessageType
            for event_id in self.bank.get(f'events.{message_type.value}s', dict()):
                event_data = EventData.from_dict(self.bank[f'{message_type.value}.{event_id}'].as_dict())
                event = Event(event_id, message_type, event_data)
                self._events[message_type, event_id] = event
    
    def save(self):
        self.bank.save()

__all__ = \
[
    'EventsBank',
]
