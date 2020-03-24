from abc import ABC
from enum import Enum
from typing import *

from dataclasses_json import LetterCase

E = TypeVar('E', bound=Enum)
def enum_encoder(letter_case: LetterCase) -> Callable[[Type[E]], Type[E]]:
    def wrapper(cls: Type[E]) -> Type[E]:
        member_map = cls._member_map_
        for e in list(cls): # type: Enum
            new_value = letter_case(e.name)
            del cls._value2member_map_[e.value]
            cls._value2member_map_[new_value] = e
            member_map[e.name]._value_ = new_value
        return cls
    return wrapper


class Dumpable(ABC):
    def dump(self) -> Iterator[str]:
        raise NotImplementedError


__all__ = \
[
    'enum_encoder',
    'Dumpable',
]
