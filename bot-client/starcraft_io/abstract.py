from abc import ABC
from typing import *

class AbstractBank(ABC):
    def reload(self):
        raise NotImplementedError
    def save(self):
        raise NotImplementedError

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')
class AbstractStorage(MutableMapping[K, V], Generic[K, V, T], ABC):
    def set_value(self, key: K, value: T):
        raise NotImplementedError
    def get_value(self, key: K, default: Optional[T] = None) -> T:
        try:
            return self._map_values(self[key])
        except KeyError:
            return default
    def get_or_create(self, key: K) -> V:
        if (not key in self):
            self[key] = self._default(key)
        return self[key]
    
    def as_dict(self) -> Dict[K, T]:
        return dict(self.dict_items())
    
    def dict_items(self) -> Iterator[Tuple[K, T]]:
        for k, v in self.items():
            yield k, self._map_values(v)
    
    def _map_values(self, v: V) -> T:
        raise NotImplementedError
    def _default(self, key: K) -> V:
        raise NotImplementedError

__all__ = \
[
    'AbstractBank',
    'AbstractStorage',
]
