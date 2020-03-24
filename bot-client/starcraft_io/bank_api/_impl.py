import os
from collections import UserDict
from dataclasses import dataclass, field
from typing import *
from xml.etree.ElementTree import *

from functional import identity

from ._bank import *

data_type_mapping = dict \
(
    string = (str, identity),
    text = (Text, lambda v: Text(v)),
    flag = (bool, lambda v: v == '1'),
    int = (int, lambda v: int(v)),
    fixed = (float, lambda v: float(v)),
    point = (Point, lambda v: Point.from_str(v)),
)

@dataclass
class BankElementImpl(BankElement, Generic[DataType]):
    key: str
    element: Element = field(repr=False)
    
    _value: DataType = field(init=False, default=None)
    _data_type: Type[DataType] = field(init=False, default=None)
    
    @property
    def value(self) -> DataType:
        return self._value
    @value.setter
    def value(self, v: DataType):
        actual = type(v)
        
        for tp in AllowedDataTypes:
            if (tp is actual):
                self._set(tp, v)
                return 
        
        for tp in AllowedDataTypes:
            if (isinstance(v, tp)):
                self._set(tp, v)
                return
        
        raise TypeError("Unable to determine data type. Please, use more strict checking")
    
    def _get(self, tp: Type[DataType]) -> DataType:
        if (self._data_type is tp):
            return self._value
        else:
            raise TypeError(f"{self} contains {self._data_type.__name__}, but {tp.__name__} was requested")
    
    def _set(self, tp: Type[DataType], v: DataType):
        self._data_type = tp
        self._value = v
    
    def _parse_data(self) -> Tuple[Type[DataType], DataType]:
        val: Optional[Element] = self.element.find('Value')
        if (val is None):
            return Unit, Unit(self.element)
        else:
            for k, v in val.attrib.items(): # type: str, str
                try:
                    tp, data_constructor = data_type_mapping[k]
                except KeyError:
                    continue
                else:
                    return tp, data_constructor(v)
            else:
                raise ValueError(f"Cannot parse element {self.element}: Unable to recognize data type")
    
    def __post_init__(self):
        self._set(*self._parse_data())
    
    def dump(self) -> Iterator[str]:
        yield f'   * Key {self.key!r}: {self._data_type.__name__} {self.value!r}'

@dataclass
class BankSectionImpl(BankSection, UserDict):
    key: str
    element: Element = field(repr=False)
    data: Dict[str, BankElementImpl] = field(init=False, default=None)
    
    def __post_init__(self):
        self.data = dict()
        for item in self.element:
            key = item.attrib['name']
            self.data[key] = BankElementImpl(key, item)
    
    def dump(self) -> Iterator[str]:
        yield f' - Section {self.key!r}:'
        for v in self.data.values():
            yield from v.dump()

B = TypeVar('B', bound='Bank')
@dataclass
class BankImpl(Bank, UserDict):
    path: str
    bank_name: str = None
    version: str = field(init=False, default='1')
    
    data: Dict[str, BankSectionImpl] = field(init=False, default=None)
    tree: ElementTree = field(init=False, default=None, repr=False)
    
    def __post_init__(self):
        if (self.bank_name is None):
            self.bank_name = os.path.basename(self.path).rpartition('.')[0]
        self.reload()
    
    def reload(self):
        if (not os.path.isfile(self.path)):
            raise FileNotFoundError(f"Path '{self.path}' does not exist")
        
        if (self.data is not None): del self.data
        if (self.tree is not None): del self.tree
        
        self.data = dict()
        self.tree = ElementTree(file=self.path)
        
        root: Element = self.tree.getroot()
        for item in root: # type: Element
            key = item.attrib['name']
            self.data[key] = BankSectionImpl(key, item)
        
        self.version = root.attrib['version']
    
    def save(self):
        raise NotImplementedError
    
    @classmethod
    def _open_file(cls, path: str) -> 'BankImpl':
        return BankImpl(path)
    
    def dump(self) -> Iterator[str]:
        yield f'Bank {self.bank_name!r}:'
        for v in self.data.values():
            yield from v.dump()


__all__ = \
[
    'BankImpl',
    'BankElementImpl',
    'BankSectionImpl',
]
