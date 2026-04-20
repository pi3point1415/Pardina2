from typing import *

from datetime import time, datetime

import main
import auto_van


class Schedule:
    def __init__(self, name : str, day : int, where_time : time | None, van_time : time):
        self.name = name
        self.day = day
        self.where_time = where_time
        self.van_time = van_time

    @property
    def is_today(self):
        return self.day == datetime.now().weekday()

    def matches_auto_van(self, auto_vans : List[auto_van.AutoVan]):
        for other in auto_vans:
            if (
                self.name == other.name and
                self.day == other.day and
                self.where_time == other.where_time and
                self.van_time == other.van_time
            ):
                return True
        return False

    def to_auto_van(self, bot : main.Pardina):
        return auto_van.AutoVan(
            bot=bot,
            name=self.name,
            day=self.day,
            where_time=self.where_time,
            van_time=self.van_time,
        )

    def serialize(self) -> Dict:
        return {
            'name': self.name,
            'day': self.day,
            'where_time': self.where_time.isoformat() if self.where_time else None,
            'van_time': self.van_time.isoformat(),
        }

    @classmethod
    def deserialize(cls, data : Dict) -> Schedule:
        return Schedule(
            name=data['name'],
            day=data['day'],
            where_time=time.fromisoformat(data['where_time']) if data['where_time'] else None,
            van_time=time.fromisoformat(data['van_time']),
        )
