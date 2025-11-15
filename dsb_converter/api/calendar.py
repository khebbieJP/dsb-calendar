"""
ICS calendar file generation functions
"""

from datetime import datetime
from pathlib import Path
from typing import Union
from icalendar import Calendar, Event
from dateutil import tz

from .models import TicketInfo


class CalendarGenerationError(Exception):
    """Raised when calendar generation fails"""
    pass


def create_ics_bytes(info: TicketInfo) -> bytes:
    """
    Create ICS calendar data from journey information.

    Args:
        info: TicketInfo object containing journey information

    Returns:
        ICS file content as bytes

    Raises:
        CalendarGenerationError: If calendar cannot be generated
    """
    if not info.is_valid():
        raise CalendarGenerationError(
            "Insufficient ticket information to create calendar event. "
            "Required: from_station, to_station, departure_date, departure_time, arrival_time"
        )

    # Create calendar
    cal = Calendar()
    cal.add('prodid', '-//DSB Transport//example.com//')
    cal.add('version', '2.0')

    # Create event
    event = Event()

    # Set start and end times (convert to UTC)
    copenhagen_tz = tz.gettz('Europe/Copenhagen')

    day, month, year = info.departure_date
    dep_hour, dep_minute = info.departure_time
    arr_hour, arr_minute = info.arrival_time

    # Create datetime objects in Copenhagen timezone
    dtstart = datetime(year, month, day, dep_hour, dep_minute, tzinfo=copenhagen_tz)
    dtend = datetime(year, month, day, arr_hour, arr_minute, tzinfo=copenhagen_tz)

    # Convert to UTC for ICS file
    dtstart_utc = dtstart.astimezone(tz.UTC)
    dtend_utc = dtend.astimezone(tz.UTC)

    event.add('dtstart', dtstart_utc)
    event.add('dtend', dtend_utc)
    event.add('dtstamp', datetime.now(tz.UTC))

    # Set UID
    date_str = dtstart.strftime('%Y%m%d')
    event.add('uid', f'dsb-rejse-{date_str}@example.com')

    # Set summary
    from_station = info.from_station or 'Unknown'
    to_station = info.to_station or 'Unknown'
    event.add('summary', f'DSB Rejse – {from_station} → {to_station}')

    # Set location
    event.add('location', f'{from_station} til {to_station}')

    # Set description
    description_parts = []
    if info.train_type and info.train_number:
        description_parts.append(f'{info.train_type} {info.train_number}')
    if info.wagon:
        description_parts.append(f'vogn {info.wagon}')
    if info.seat:
        description_parts.append(f'plads {info.seat}')
    if info.travel_class:
        description_parts.append(info.travel_class)
    if info.price:
        description_parts.append(f'pris {info.price} kr.')

    event.add('description', ', '.join(description_parts))
    event.add('categories', 'Travel')

    # Add event to calendar
    cal.add_component(event)

    return cal.to_ical()


def create_ics_file(info: TicketInfo, output_path: Union[str, Path]) -> None:
    """
    Create an ICS calendar file from journey information.

    Args:
        info: TicketInfo object containing journey information
        output_path: Path where the ICS file should be saved

    Raises:
        CalendarGenerationError: If calendar cannot be generated
    """
    ics_data = create_ics_bytes(info)

    output_path = Path(output_path)
    output_path.write_bytes(ics_data)
