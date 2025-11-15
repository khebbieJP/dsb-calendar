"""
PDF parsing functions for extracting DSB ticket information
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Union
import pdfplumber

from .models import TicketInfo
from .utils import parse_danish_month
from .constants import TRAIN_TYPES, TRAVEL_CLASS_FIRST, TRAVEL_CLASS_SECOND


class TicketParsingError(Exception):
    """Raised when ticket parsing fails"""
    pass


def extract_ticket_info(pdf_path: Union[str, Path]) -> TicketInfo:
    """
    Extract journey information from DSB ticket PDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        TicketInfo object containing extracted information

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        TicketParsingError: If PDF cannot be parsed
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Extract text from all pages
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"
    except Exception as e:
        raise TicketParsingError(f"Failed to read PDF: {e}")

    if not full_text.strip():
        raise TicketParsingError("PDF contains no extractable text")

    info = TicketInfo()

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

        info.departure_date = (int(day), month, year)
        info.departure_time = (int(hour), int(minute))

    # Extract stations - looking for common Danish station names
    # Pattern to find the journey line with stations (supports H, St., M, and other suffixes)
    station_pattern = r'(\d{1,2})\.(jan|feb|mar|apr|maj|jun|jul|aug|sep|okt|nov|dec)\.\s+(\d{1,2}):(\d{2})\s+([\w\s]+?(?:H|St\.|M))\s+([\w\s]+?(?:H|St\.|M))\s+\d{1,2}\.(jan|feb|mar|apr|maj|jun|jul|aug|sep|okt|nov|dec)\.\s+(\d{1,2}):(\d{2})'
    station_match = re.search(station_pattern, full_text, re.IGNORECASE)

    if station_match:
        info.from_station = station_match.group(5).strip()
        info.to_station = station_match.group(6).strip()
        info.arrival_time = (int(station_match.group(8)), int(station_match.group(9)))
    else:
        # Fallback: look for explicit station names in "Fra: X" and "Til: Y" format
        # Match stations ending in H, St., M or other common patterns
        from_pattern = r'Fra:\s+([\w\s]+?(?:H|St\.|M))(?:\s|$)'
        to_pattern = r'Til:\s+([\w\s]+?(?:H|St\.|M))(?:\s|$|,)'
        from_match = re.search(from_pattern, full_text, re.IGNORECASE)
        to_match = re.search(to_pattern, full_text, re.IGNORECASE)

        if from_match and to_match:
            info.from_station = from_match.group(1).strip()
            info.to_station = to_match.group(1).strip()
        else:
            # Last fallback: look for station names in travel plan section
            # This handles the format "København H - Skanderborg St."
            route_pattern = r'([\w\s]+?(?:H|St\.|M))\s*-\s*([\w\s]+?(?:H|St\.|M))'
            route_match = re.search(route_pattern, full_text, re.IGNORECASE)
            if route_match:
                info.from_station = route_match.group(1).strip()
                info.to_station = route_match.group(2).strip()

    # Extract arrival time if not found
    if not info.arrival_time:
        time_pattern = r'(\d{1,2}):(\d{2})'
        times = re.findall(time_pattern, full_text)
        if len(times) >= 2:
            info.arrival_time = (int(times[1][0]), int(times[1][1]))

    # Extract train information
    train_types_pattern = '|'.join(TRAIN_TYPES)
    train_pattern = rf'({train_types_pattern})\s+(\d+)'
    train_match = re.search(train_pattern, full_text, re.IGNORECASE)
    if train_match:
        info.train_type = train_match.group(1)
        info.train_number = train_match.group(2)

    # Extract wagon and seat
    # First try to extract from table format: "InterCityLyn 42 91 22"
    if info.train_type and info.train_number:
        train_data_pattern = rf'{info.train_type}\s+{info.train_number}\s+(\d+)\s+(\d+)'
        train_data_match = re.search(train_data_pattern, full_text, re.IGNORECASE)
        if train_data_match:
            info.wagon = train_data_match.group(1)
            info.seat = train_data_match.group(2)

    # Fallback: look for explicit labels
    if not info.wagon:
        wagon_pattern = r'Vognnr\.?\s+(\d+)'
        wagon_match = re.search(wagon_pattern, full_text)
        if wagon_match:
            info.wagon = wagon_match.group(1)

    if not info.seat:
        seat_pattern = r'Pladsnr\.?\s+(\d+)'
        seat_match = re.search(seat_pattern, full_text)
        if seat_match:
            info.seat = seat_match.group(1)

    # Extract class
    class_pattern = r'(DSB 1\'|DSB 2\'|1\. klasse|2\. klasse)'
    class_match = re.search(class_pattern, full_text, re.IGNORECASE)
    if class_match:
        class_text = class_match.group(1)
        if '1' in class_text:
            info.travel_class = TRAVEL_CLASS_FIRST
        else:
            info.travel_class = TRAVEL_CLASS_SECOND

    # Extract price
    price_pattern = r'(\d+)\s*kr\.'
    price_matches = re.findall(price_pattern, full_text)
    if price_matches:
        info.price = price_matches[0]

    return info
