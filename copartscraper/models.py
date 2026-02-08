from dataclasses import dataclass
import datetime


@dataclass
class LotData:
    image_id: str
    lot_url: str
    id: int
    name: str
    odometer: str
    conditions: 'CarCondition'
    auction: str
    start_date: 'datetime.datetime'
    last_check: 'datetime.datetime'
    current_bid: int
    buy_now: int

    def as_tuple(self):
        return (
            self.image_id,
            self.lot_url,
            self.id,
            self.name,
            self.odometer,
            self.conditions,
            self.auction,
            self.start_date,
            self.current_bid,
            self.buy_now,
        )


@dataclass
class CarCondition:
    title: str
    condition1: str
    condition2: str

    @classmethod
    def from_str(cls, s: str):
        parts = s.split("|")
        return cls(parts[0].strip(), parts[1].strip(), parts[2].strip())

    def __str__(self):
        return f"{self.title} | {self.condition1} | {self.condition2}"

    def __eq__(self, other):
        if not isinstance(other, CarCondition):
            return NotImplemented
        return (
            self.title == other.title and
            self.condition1 == other.condition1 and
            self.condition2 == other.condition2
        )

    def __ne__(self, other):
        if not isinstance(other, CarCondition):
            return True
        return not (self == other)
