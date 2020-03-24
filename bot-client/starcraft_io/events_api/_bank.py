from dataclasses import dataclass, field
from typing import *

from ..abstract import *
from ..bank_api import *
from ..util import filter_out
from ._model import *
from ._events import *

@dataclass
class EventsBank(AbstractBank):
    bank: Bank = field(repr=False)
    meta: MetaData = field(init=False)
    
    def __post_init__(self):
        self.reload()
    
    def _get_event(self, event_id: str, message_type: MessageType, *, pop: bool = False) -> Event:
        getter: Callable[[str], BankSection]
        if (pop):
            getter = self.bank.pop
        else:
            getter = self.bank.get
        
        event_data = EventData.from_dict(getter(Literals.get_event_key(event_id, message_type)).as_dict())
        event_type = EVENT_MAPPING[event_data.event_type]
        event = event_type(event_id=event_id, message_type=message_type, event_data=event_data)
        return event
    
    def add_event(self, event: Event):
        self.bank.set_value(Literals.get_event_key(event.event_id, event.message_type), filter_out(event.event_data.to_dict(encode_json=True)))
        ids_list = self.bank.get_or_create(Literals.get_event_list_key(event.message_type))
        ids_list.set_value(event.event_id, event.event_id)
    
    def get_event(self, event_id: str, message_type: MessageType) -> Event:
        return self._get_event(event_id, message_type, pop=False)
    def pop_event(self, event_id: str, message_type: MessageType) -> Event:
        return self._get_event(event_id, message_type, pop=True)
    
    def event_ids(self, message_type: MessageType, *, pop: bool = False) -> Iterable[str]:
        getter: Callable[[str], BankSection]
        if (pop):
            getter = self.bank.pop
        else:
            getter = self.bank.get
        
        return getter(Literals.get_event_list_key(message_type), dict()).keys()
    
    def reload(self):
        self.bank.reload()
        self.meta = MetaData.from_dict(self.bank[Literals.MetaSectionKey.value].as_dict())
    
    def save(self):
        self.bank.save()

__all__ = \
[
    'EventsBank',
]
