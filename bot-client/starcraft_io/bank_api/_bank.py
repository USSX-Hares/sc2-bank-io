from abc import ABC
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import *
from xml.etree.ElementTree import Element

from ..abstract import *
from ..util import Dumpable

class Text(str): pass

@dataclass
class Unit:
    xml: Element

@dataclass
class Point:
    x: float
    y: float
    
    @classmethod
    def from_str(cls, s: str) -> 'Point':
        return cls(*map(float, s.split(',')))
    def to_str(self) -> str:
        return f'{self.x},{self.y}'

AllowedDataTypes = [ str, int, float, bool, Text, Point, Unit ]
DataType = TypeVar('DataType', *AllowedDataTypes)

@wraps(property)
def _make_property(tp: Type[DataType]) -> Callable[[Any], property]:
    @property
    def prop(self: 'BankElement') -> DataType:
        return self._get(tp)
    
    @prop.setter
    def prop(self: 'BankElement', data: tp):
        return self._set(tp, data)
    
    return lambda _: prop

class BankElement(Generic[DataType], Dumpable, ABC):
    key: str
    value: DataType
    
    @property
    def data_type(self) -> Type[DataType]:
        raise NotImplementedError
    
    def _get(self, tp: Type[DataType]) -> DataType:
        if (self._data_type is tp):
            return self._value
        else:
            raise TypeError(f"{self} contains {self._data_type.__name__}, but {tp.__name__} was requested")
    
    def _set(self, tp: Type[DataType], v: DataType):
        self._data_type = tp
        self._value = v
    
    @_make_property(str)
    def string_value(self): pass
    
    @_make_property(Text)
    def text_value(self): pass
    
    @_make_property(bool)
    def flag_value(self): pass
    
    @_make_property(int)
    def int_value(self): pass
    
    @_make_property(float)
    def fixed_value(self): pass
    
    @_make_property(Point)
    def point_value(self): pass
    
    @_make_property(Unit)
    def unit_value(self): pass

class BankSection(AbstractStorage[str, BankElement, DataType], Dumpable, ABC):
    key: str
    
    def _map_values(self, v: BankElement) -> DataType:
        return v.value


B = TypeVar('B', bound='Bank')
T = TypeVar('T')
class Bank(AbstractStorage[str, BankSection, Dict[str, DataType]], AbstractBank, Dumpable, ABC):
    version: str
    path: str
    
    @classmethod
    def _open_file(cls, path: str) -> 'Bank':
        raise NotImplementedError
    
    @classmethod
    def get_bank_filename(cls, bank_name: str, *, account_id: str = None, player_id: str = None, publisher_id: str = None, starcraft_name: str = 'StarCraft II', test_run: bool = False) -> str:
        p = Path.home().joinpath('Documents', starcraft_name)
        if (not test_run):
            assert account_id is not None,   ValueError(f"'account_id' should not be {None} when 'test_run' is {False}")
            assert player_id is not None,    ValueError(f"'player_id' should not be {None} when 'test_run' is {False}")
            assert publisher_id is not None, ValueError(f"'publisher_id' should not be {None} when 'test_run' is {False}")
            p = p.joinpath('Accounts', account_id, player_id, 'Banks', publisher_id)
        else:
            p = p.joinpath('Banks')
        
        return str(p.joinpath(f'{bank_name}.SC2Bank'))
    
    @classmethod
    @overload
    def open(cls: Type[B], path: str) -> 'Bank':
        pass
    @classmethod
    @overload
    def open(cls: Type[B], bank_name: str, *, account_id: str = None, player_id: str = None, publisher_id: str = None, starcraft_name: str = 'StarCraft II', test_run: bool = False) -> 'Bank':
        pass
    @classmethod
    def open(cls: Type[B], *args, **kwargs) -> B:
        total_args = len(args) + len(kwargs)
        if (total_args == 1):
            return cls._open_file(*args, **kwargs)
        elif (total_args in range(1, 7)):
            return cls._open_file(cls.get_bank_filename(*args, **kwargs))
        else:
            raise TypeError(f"Wrong number of arguments passed to {cls.open.__name__}: Expected either 1, 4 or 5; got {total_args}")
    
    def _map_values(self, v: BankSection) -> Dict[str, DataType]:
        return v.as_dict()

__all__ = \
[
    'AllowedDataTypes',
    'Bank',
    'BankElement',
    'BankSection',
    'DataType',
    'Point',
    'Text',
    'Unit',
]
