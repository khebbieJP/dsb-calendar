#!/usr/bin/env python3
"""
DSB Ticket PDF to ICS Calendar Converter

This script extracts train journey information from a DSB ticket PDF
and generates an ICS calendar file.
"""

import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pdfplumber
from icalendar import Calendar, Event
from dateutil import tz


def parse_danish_month(month_abbr):
    """Convert Danish month abbreviation to month number."""
    months = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
        'maj': 5, 'jun': 6, 'jul': 7, 'aug': 8,
        'sep': 9, 'okt': 10, 'nov': 11, 'dec': 12
    }
    return months.get(month_abbr.lower(), None)


def extract_ticket_info(pdf_path):
    """Extract journey information from DSB ticket PDF."""

    with pdfplumber.open(pdf_path) as pdf:
        # Extract text from all pages
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"

    info = {}

    # Extract date - looking for pattern like "14.nov. 13:15"
    date_pattern = r'(\d{1,2})\.(jan|feb|mar|apr|maj|jun|jul|aug|sep|okt|nov|dec)\.\s+(\d{1,2}):(\d{2})'
    date_matches = re.findall(date_pattern, full_text, re.IGNORECASE)

    if date_matches:
        day, month_abbr, hour, minute = date_matches[0]
        month = parse_danish_month(month_abbr)

        # Try to extract year from booking date or use current/next year
        year_pattern = r'(\d{2})\.(\d{2})\.(\d{2})\s+(\d{2}):(\d{2})'
        year_match = re.search(year_pattern, full_text)

        if year_match:
            booking_year = 2000 + int(year_match.group(3))
            # If the journey month is before current month, assume next year
            current_date = datetime.now()
            year = booking_year
            if month < current_date.month and booking_year == current_date.year:
                year = booking_year + 1
        else:
            # Default to current year or next year if month has passed
            current_date = datetime.now()
            year = current_date.year
            if month < current_date.month:
                year += 1

        info['departure_date'] = (int(day), month, year)
        info['departure_time'] = (int(hour), int(minute))

    # Extract stations - looking for common Danish station names
    # Pattern to find the journey line with stations
    station_pattern = r'(\d{1,2})\.(jan|feb|mar|apr|maj|jun|jul|aug|sep|okt|nov|dec)\.\s+(\d{1,2}):(\d{2})\s+([\w\s]+?H)\s+([\w\s]+?H)\s+\d{1,2}\.(jan|feb|mar|apr|maj|jun|jul|aug|sep|okt|nov|dec)\.\s+(\d{1,2}):(\d{2})'
    station_match = re.search(station_pattern, full_text, re.IGNORECASE)

    if station_match:
        info['from_station'] = station_match.group(5).strip()
        info['to_station'] = station_match.group(6).strip()
        info['arrival_time'] = (int(station_match.group(8)), int(station_match.group(9)))
    else:
        # Fallback: look for explicit station names in "Fra: X" and "Til: Y" format
        from_pattern = r'Fra:\s+([\w\s]+H)'
        to_pattern = r'Til:\s+([\w\s]+H)'
        from_match = re.search(from_pattern, full_text, re.IGNORECASE)
        to_match = re.search(to_pattern, full_text, re.IGNORECASE)

        if from_match and to_match:
            info['from_station'] = from_match.group(1).strip()
            info['to_station'] = to_match.group(1).strip()
        else:
            # Last fallback: common station names
            station_names = r'(Aarhus H|København H|Aalborg|Odense M|Fredericia St)'
            stations = re.findall(station_names, full_text)
            if len(stations) >= 2:
                info['from_station'] = stations[0]
                info['to_station'] = stations[1]

    # Extract arrival time if not found
    if 'arrival_time' not in info:
        time_pattern = r'(\d{1,2}):(\d{2})'
        times = re.findall(time_pattern, full_text)
        if len(times) >= 2:
            info['arrival_time'] = (int(times[1][0]), int(times[1][1]))

    # Extract train information
    train_pattern = r'(InterCityLyn|InterCity|Regionaltog|Lyn)\s+(\d+)'
    train_match = re.search(train_pattern, full_text, re.IGNORECASE)
    if train_match:
        info['train_type'] = train_match.group(1)
        info['train_number'] = train_match.group(2)

    # Extract wagon and seat
    # First try to extract from table format: "InterCityLyn 42 91 22"
    if 'train_type' in info and 'train_number' in info:
        train_data_pattern = rf'{info["train_type"]}\s+{info["train_number"]}\s+(\d+)\s+(\d+)'
        train_data_match = re.search(train_data_pattern, full_text, re.IGNORECASE)
        if train_data_match:
            info['wagon'] = train_data_match.group(1)
            info['seat'] = train_data_match.group(2)

    # Fallback: look for explicit labels
    if 'wagon' not in info:
        wagon_pattern = r'Vognnr\.?\s+(\d+)'
        wagon_match = re.search(wagon_pattern, full_text)
        if wagon_match:
            info['wagon'] = wagon_match.group(1)

    if 'seat' not in info:
        seat_pattern = r'Pladsnr\.?\s+(\d+)'
        seat_match = re.search(seat_pattern, full_text)
        if seat_match:
            info['seat'] = seat_match.group(1)

    # Extract class
    class_pattern = r'(DSB 1\'|DSB 2\'|1\. klasse|2\. klasse)'
    class_match = re.search(class_pattern, full_text, re.IGNORECASE)
    if class_match:
        class_text = class_match.group(1)
        if '1' in class_text:
            info['class'] = '1. klasse'
        else:
            info['class'] = '2. klasse'

    # Extract price
    price_pattern = r'(\d+)\s*kr\.'
    price_matches = re.findall(price_pattern, full_text)
    if price_matches:
        info['price'] = price_matches[0]

    return info


def create_ics_file(info, output_path):
    """Create an ICS calendar file from journey information."""

    # Create calendar
    cal = Calendar()
    cal.add('prodid', '-//DSB Transport//example.com//')
    cal.add('version', '2.0')

    # Create event
    event = Event()

    # Set start and end times (convert to UTC)
    copenhagen_tz = tz.gettz('Europe/Copenhagen')

    day, month, year = info['departure_date']
    dep_hour, dep_minute = info['departure_time']
    arr_hour, arr_minute = info['arrival_time']

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
    from_station = info.get('from_station', 'Unknown')
    to_station = info.get('to_station', 'Unknown')
    event.add('summary', f'DSB Rejse – {from_station} → {to_station}')

    # Set location
    event.add('location', f'{from_station} til {to_station}')

    # Set description
    train_type = info.get('train_type', '')
    train_number = info.get('train_number', '')
    wagon = info.get('wagon', '')
    seat = info.get('seat', '')
    class_type = info.get('class', '')
    price = info.get('price', '')

    description_parts = []
    if train_type and train_number:
        description_parts.append(f'{train_type} {train_number}')
    if wagon:
        description_parts.append(f'vogn {wagon}')
    if seat:
        description_parts.append(f'plads {seat}')
    if class_type:
        description_parts.append(class_type)
    if price:
        description_parts.append(f'pris {price} kr.')

    event.add('description', ', '.join(description_parts))
    event.add('categories', 'Travel')

    # Add event to calendar
    cal.add_component(event)

    # Write to file
    with open(output_path, 'wb') as f:
        f.write(cal.to_ical())

    print(f"ICS file created: {output_path}")


def main():
    """Main function to process DSB ticket PDF and create ICS file."""

    if len(sys.argv) < 2:
        print("Usage: python dsb_to_ics.py <input_pdf> [output_ics]")
        print("Example: python dsb_to_ics.py Billet.pdf DSB_Rejse_2025-11-14.ics")
        sys.exit(1)

    input_pdf = sys.argv[1]

    # Generate output filename if not provided
    if len(sys.argv) >= 3:
        output_ics = sys.argv[2]
    else:
        pdf_path = Path(input_pdf)
        output_ics = pdf_path.with_suffix('.ics').name

    # Check if input file exists
    if not Path(input_pdf).exists():
        print(f"Error: File '{input_pdf}' not found.")
        sys.exit(1)

    print(f"Processing: {input_pdf}")

    # Extract information from PDF
    try:
        info = extract_ticket_info(input_pdf)

        # Display extracted information
        print("\nExtracted Information:")
        print(f"  From: {info.get('from_station', 'N/A')}")
        print(f"  To: {info.get('to_station', 'N/A')}")

        if 'departure_date' in info:
            day, month, year = info['departure_date']
            dep_hour, dep_minute = info['departure_time']
            print(f"  Departure: {year}-{month:02d}-{day:02d} {dep_hour:02d}:{dep_minute:02d}")

        if 'arrival_time' in info:
            arr_hour, arr_minute = info['arrival_time']
            print(f"  Arrival: {arr_hour:02d}:{arr_minute:02d}")

        if 'train_type' in info and 'train_number' in info:
            print(f"  Train: {info['train_type']} {info['train_number']}")

        if 'wagon' in info:
            print(f"  Wagon: {info['wagon']}")

        if 'seat' in info:
            print(f"  Seat: {info['seat']}")

        if 'class' in info:
            print(f"  Class: {info['class']}")

        if 'price' in info:
            print(f"  Price: {info['price']} kr.")

        # Create ICS file
        print(f"\nCreating ICS file...")
        create_ics_file(info, output_ics)

        print("\nDone!")

    except Exception as e:
        print(f"Error processing PDF: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
