from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Abstract Base Class for Repositories."""
    
    @abstractmethod
    def add(self, item: T) -> T:
        pass
        
    @abstractmethod
    def get(self, id: int) -> Optional[T]:
        pass
        
    @abstractmethod
    def list(self) -> List[T]:
        pass
