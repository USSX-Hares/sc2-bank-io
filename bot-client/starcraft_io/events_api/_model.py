from abc import ABC
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import *
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, dataclass_json, LetterCase

from ..util import enum_encoder

@enum_encoder(LetterCase.KEBAB)
class EventType(Enum):
    Ping = auto()
    Disconnection = auto()
    AllocateUnit = auto()
    IssueOrder = auto()
    RevokeOwner = auto()
    UnitDies = auto()

@enum_encoder(LetterCase.KEBAB)
class MessageType(Enum):
    Request = auto()
    Response = auto()

@dataclass
@dataclass_json(letter_case=LetterCase.KEBAB)
class EventData(DataClassJsonMixin):
    event_type: EventType
    success: Optional[bool] = None
    custom_data: Optional[str] = None
    unit_id: Optional[str] = None
    owner_id: Optional[str] = None

@dataclass
@dataclass_json(letter_case=LetterCase.KEBAB)
class MetaData(DataClassJsonMixin):
    protocol_version: str
    game_id: str
    start_time: str

T = TypeVar('T')
@dataclass
class Event(ABC):
    event_id: str
    message_type: MessageType
    event_data: EventData
    
    @property
    def error(self):
        if (self.message_type == MessageType.Response and not self.event_data.success):
            return self.event_data.custom_data
        else:
            raise ValueError(f"Error message available only for failure responses")
    
    _associated_event_type: EventType = field(init=False, repr=False, compare=False)
    @classmethod
    def _new(cls: Type[T], **kwargs) -> T:
        kwargs.setdefault('event_id', str(uuid4()))
        kwargs.setdefault('event_data', EventData(cls._associated_event_type))
        return cls(**kwargs)
    @classmethod
    def new_request(cls: Type[T], **kwargs) -> T:
        kwargs['message_type'] = MessageType.Request
        return cls._new(**kwargs)
    @classmethod
    def new_response(cls: Type[T], **kwargs) -> T:
        kwargs['message_type'] = MessageType.Response
        return cls._new(**kwargs)


class Literals(Enum):
    EventsListSectionKeyPrefix = 'events'
    MetaSectionKey = 'meta'
    
    @classmethod
    def get_event_key(cls, event_id, message_type: MessageType) -> str:
        return f'{message_type.value}.{event_id}'
    
    @classmethod
    def get_event_list_key(cls, message_type: MessageType) -> str:
        return f'{cls.EventsListSectionKeyPrefix.value}.{message_type.value}s'

__all__ = \
[
    'Event',
    'EventData',
    'EventType',
    'MessageType',
    'MetaData',
    'Literals',
]
