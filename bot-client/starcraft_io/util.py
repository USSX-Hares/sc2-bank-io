from abc import ABC
from enum import Enum
from types import MappingProxyType
from typing import *

from dataclasses_json import LetterCase

E = TypeVar('E', bound=Type[Enum])
def enum_encoder(letter_case: LetterCase) -> Callable[[E], E]:
    def wrapper(cls: E) -> E:
        member_map = cls._member_map_
        for e in list(cls): # type: Enum
            new_value = letter_case(e.name)
            del cls._value2member_map_[e.value]
            cls._value2member_map_[new_value] = e
            member_map[e.name]._value_ = new_value
        return cls
    return wrapper

K = TypeVar('K')
V = TypeVar('V')
def filter_out(d: Dict[K, Optional[V]]) -> Dict[K, V]:
    return dict(filter_out_iter(d))
def filter_out_iter(d: Dict[K, Optional[V]]) -> Iterator[Tuple[K, V]]:
    for k, v in d.items():
        if (v is not None):
            yield k, v


class MappingProxy(Mapping, Generic[K, V]):
    def __init__(self, getter: Callable[[K], V], iterator: Callable[[], Iterator[K]]):
        self._getitem = getter
        self._iter = iterator
    
    def __getitem__(self, item):
        return self._getitem(item)
    def __iter__(self):
        return self._iter()
    def __len__(self):
        return len(list(iter(self)))


class Dumpable(ABC):
    def dump(self) -> Iterator[str]:
        raise NotImplementedError


__all__ = \
[
    'enum_encoder',
    'filter_out',
    'filter_out_iter',
    'Dumpable',
    'MappingProxy',
]
