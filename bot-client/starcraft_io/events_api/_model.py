from dataclasses import dataclass
from enum import Enum, auto
from typing import *

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

@dataclass
class Event:
    event_id: str
    message_type: MessageType
    event_data: EventData


__all__ = \
[
    'Event',
    'EventData',
    'EventType',
    'MessageType',
    'MetaData',
]
