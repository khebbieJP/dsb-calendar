"""
Data models for DSB ticket information
"""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class TicketInfo:
    """Represents extracted information from a DSB ticket"""

    from_station: Optional[str] = None
    to_station: Optional[str] = None
    departure_date: Optional[Tuple[int, int, int]] = None  # (day, month, year)
    departure_time: Optional[Tuple[int, int]] = None  # (hour, minute)
    arrival_time: Optional[Tuple[int, int]] = None  # (hour, minute)
    train_type: Optional[str] = None
    train_number: Optional[str] = None
    wagon: Optional[str] = None
    seat: Optional[str] = None
    travel_class: Optional[str] = None
    price: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            'from_station': self.from_station,
            'to_station': self.to_station,
            'departure_date': self.departure_date,
            'departure_time': self.departure_time,
            'arrival_time': self.arrival_time,
            'train_type': self.train_type,
            'train_number': self.train_number,
            'wagon': self.wagon,
            'seat': self.seat,
            'class': self.travel_class,
            'price': self.price,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create TicketInfo from dictionary"""
        return cls(
            from_station=data.get('from_station'),
            to_station=data.get('to_station'),
            departure_date=data.get('departure_date'),
            departure_time=data.get('departure_time'),
            arrival_time=data.get('arrival_time'),
            train_type=data.get('train_type'),
            train_number=data.get('train_number'),
            wagon=data.get('wagon'),
            seat=data.get('seat'),
            travel_class=data.get('class'),
            price=data.get('price'),
        )

    def is_valid(self) -> bool:
        """Check if ticket has minimum required information"""
        return all([
            self.from_station,
            self.to_station,
            self.departure_date,
            self.departure_time,
            self.arrival_time,
        ])

    def get_formatted_departure(self) -> Optional[str]:
        """Get formatted departure date and time"""
        if not self.departure_date or not self.departure_time:
            return None
        day, month, year = self.departure_date
        hour, minute = self.departure_time
        return f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"

    def get_formatted_arrival(self) -> Optional[str]:
        """Get formatted arrival time"""
        if not self.arrival_time:
            return None
        hour, minute = self.arrival_time
        return f"{hour:02d}:{minute:02d}"
