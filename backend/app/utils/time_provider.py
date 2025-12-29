"""
Time provider utilities for dependency injection to enable testability.
"""
import time
from datetime import datetime
from abc import ABC, abstractmethod


class TimeProvider(ABC):
    """Abstract base class for time operations."""
    
    @abstractmethod
    def time(self) -> float:
        """Get current time as a timestamp."""
        pass
    
    @abstractmethod
    def sleep(self, seconds: float) -> None:
        """Sleep for the given number of seconds."""
        pass


class SystemTimeProvider(TimeProvider):
    """Default time provider using system time."""
    
    def time(self) -> float:
        return time.time()
    
    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)


class DatetimeProvider(ABC):
    """Abstract base class for datetime operations."""
    
    @abstractmethod
    def now(self) -> datetime:
        """Get current datetime."""
        pass


class SystemDatetimeProvider(DatetimeProvider):
    """Default datetime provider using system datetime."""
    
    def now(self) -> datetime:
        return datetime.now()

