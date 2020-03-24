import os
from collections import UserDict
from dataclasses import dataclass, field
from enum import Enum
from io import BytesIO
from typing import *
from xml.dom.minidom import parseString
from xml.etree.ElementTree import *

from functional import identity

from ._bank import *

class Literals(Enum):
    BankTagName = 'Bank'
    BankVersionAttributeName = 'version'
    
    SectionTagName = 'Section'
    SectionNameAttributeName = 'name'
    
    KeyTagName = 'Key'
    KeyNameAttributeTagName = 'name'
    
    ValueTagName = 'Value'
    ValueStringAttributeName = 'string'
    ValueTextAttributeName = 'text'
    ValueFlagAttributeName = 'flag'
    ValueIntAttributeName = 'int'
    ValueFixedAttributeName = 'fixed'
    ValuePointAttributeName = 'point'

DATA_TYPE_MAPPING: Dict[str, Tuple[Type[DataType], Callable[[str], DataType]]] = \
{
    Literals.ValueStringAttributeName.value: (str, identity),
    Literals.ValueTextAttributeName.value: (Text, lambda v: Text(v)),
    Literals.ValueFlagAttributeName.value: (bool, lambda v: v == '1'),
    Literals.ValueIntAttributeName.value: (int, lambda v: int(v)),
    Literals.ValueFixedAttributeName.value: (float, lambda v: float(v)),
    Literals.ValuePointAttributeName.value: (Point, lambda v: Point.from_str(v)),
}

DATA_TYPE_REVERSED_MAPPING: Dict[Type[DataType], Tuple[str, Callable[[DataType], str]]] = \
{
    str: (Literals.ValueStringAttributeName.value, identity),
    Text: (Literals.ValueTextAttributeName.value, identity),
    bool: (Literals.ValueFlagAttributeName.value, lambda v: '1' if v else '0'),
    int: (Literals.ValueIntAttributeName.value, lambda v: str(v)),
    float: (Literals.ValueFixedAttributeName.value, lambda v: str(v)),
    Point: (Literals.ValuePointAttributeName.value, lambda v: Point.from_str(v)),
}

@dataclass
class BankElementImpl(BankElement, Generic[DataType]):
    key: str
    element: Element = field(repr=False)
    
    _value: DataType = field(init=False, default=None)
    _data_type: Type[DataType] = field(init=False, default=None)
    
    @property
    def data_type(self) -> Type[DataType]:
        return self._data_type
    
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
        val: Optional[Element] = self.element.find(Literals.ValueTagName.value)
        if (val is None):
            return Unit, Unit(self.element)
        else:
            for k, v in val.attrib.items(): # type: str, str
                try:
                    tp, data_constructor = DATA_TYPE_MAPPING[k]
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
    
    def make_element(self) -> Element:
        self.element.clear()
        self.element.attrib[Literals.KeyNameAttributeTagName.value] = self.key
        
        if (self.data_type is Unit):
            self.element.append(self.value)
        else:
            attrib_name, value_constructor = DATA_TYPE_REVERSED_MAPPING[self.data_type]
            self.element.append(self.element.makeelement(Literals.ValueTagName.value, { attrib_name: value_constructor(self.value) }))
        
        return self.element

@dataclass
class BankSectionImpl(BankSection, UserDict):
    key: str
    element: Element = field(repr=False)
    data: Dict[str, BankElementImpl] = field(init=False, default=None)
    
    def __post_init__(self):
        self.data = dict()
        for item in self.element:
            key = item.attrib[Literals.KeyNameAttributeTagName.value]
            self.data[key] = BankElementImpl(key, item)
    
    def dump(self) -> Iterator[str]:
        yield f' - Section {self.key!r}:'
        for v in self.data.values():
            yield from v.dump()
    
    def set_value(self, key: str, value: DataType):
        self.get_or_create(key).value = value
    
    def _default(self, key: str) -> BankElementImpl:
        el = self.element.makeelement(Literals.KeyTagName.value, { Literals.KeyNameAttributeTagName.value: key })
        el.append(Element(Literals.ValueTagName.value, dict(string='empty')))
        return BankElementImpl(key, el)
    
    def make_element(self) -> Element:
        self.element.clear()
        self.element.attrib[Literals.SectionNameAttributeName.value] = self.key
        
        for key, value in self.data.items():
            self.element.append(value.make_element())
        
        return self.element

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
            key = item.attrib[Literals.SectionNameAttributeName.value]
            self.data[key] = BankSectionImpl(key, item)
        
        self.version = root.attrib[Literals.BankVersionAttributeName.value]
    
    def make_element(self) -> Element:
        root: Element = self.tree.getroot()
        root.clear()
        root.attrib[Literals.BankVersionAttributeName.value] = self.version
        
        for key, value in self.data.items():
            root.append(value.make_element())
        
        return root
    
    def save(self):
        self.make_element()
        with BytesIO() as text_io:
            self.tree.write(text_io, xml_declaration=True)
            with open(self.path, 'wb') as f:
                f.write(parseString(text_io.getvalue()).toprettyxml(encoding='utf-8'))
    
    @classmethod
    def _open_file(cls, path: str) -> 'BankImpl':
        return BankImpl(path)
    
    def dump(self) -> Iterator[str]:
        yield f'Bank {self.bank_name!r}:'
        for v in self.data.values():
            yield from v.dump()
    
    def set_value(self, key: str, value: Dict[str, DataType]):
        section = self.get_or_create(key)
        for k, v in value.items():
            section.set_value(k, v)
    
    def _default(self, key: str) -> BankSection:
        return BankSectionImpl(key, self.tree.getroot().makeelement(Literals.SectionTagName.value, { Literals.SectionNameAttributeName.value: key }))


__all__ = \
[
    'DATA_TYPE_MAPPING',
    'DATA_TYPE_REVERSED_MAPPING',
    
    'BankElementImpl',
    'BankImpl',
    'BankSectionImpl',
    'Literals',
]
