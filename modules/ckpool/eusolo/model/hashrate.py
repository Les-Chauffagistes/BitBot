import re
from typing import TYPE_CHECKING, SupportsInt
if TYPE_CHECKING:
    from .worker import Worker
    from .pool import Pool


class Hashrate:
    __slots__ = ('_one_minute', '_five_minutes', '_one_hour', '_one_day', '_one_week')
    class Unit(SupportsInt):
        __slots__ = ("value",)
        def __init__(self, value: str):
            self.value = value
        
        def _suffix_to_decimal(self, value: str) -> float | int:
            if re.match("^\\d+$", value):
                return float(value)
            decimal_value = float(value[0:-1])
            suffix = value[-1].upper()
            match suffix:
                case "T":
                    decimal_value *= 1e12

                case "G":
                    decimal_value *= 1e9

                case "M":
                    decimal_value *= 1e6

                case "K":
                    decimal_value *= 1e3
                
                case _:
                    raise ValueError("Unknown suffix")
            
            return round(decimal_value)
        
        def __int__(self) -> int:
            return round(self._suffix_to_decimal(self.value))
        
        def __str__(self):
            return self.value

    def __init__(self, one_minute: str, five_minutes: str, one_hour: str, one_day: str, one_week: str):
        self.one_minute = one_minute
        self.five_minutes = five_minutes
        self.one_hour = one_hour
        self.one_day = one_day
        self.one_week = one_week

    @classmethod
    def from_json(cls, data: 'Pool.RawPool | Worker.RawWorker'):
        return cls(data['hashrate1m'], data['hashrate5m'], data['hashrate1hr'], data['hashrate1d'], data['hashrate7d'])
    
    @property
    def one_minute(self):
        return self._one_minute

    @one_minute.setter
    def one_minute(self, value: str | float):
        if isinstance(value, str):
            self._one_minute = self.Unit(value)

    @property
    def five_minutes(self):
        return self._five_minutes

    @five_minutes.setter
    def five_minutes(self, value):
        self._five_minutes = self.Unit(value)

    @property
    def one_hour(self):
        return self._one_hour

    @one_hour.setter
    def one_hour(self, value):
        self._one_hour = self.Unit(value)

    @property
    def one_day(self):
        return self._one_day

    @one_day.setter
    def one_day(self, value):
        self._one_day = self.Unit(value)

    @property
    def one_week(self):
        return self._one_week

    @one_week.setter
    def one_week(self, value):
        self._one_week = self.Unit(value)