#!/usr/bin/env python3
"""
Automated tests for DSB ticket PDF to ICS converter
"""

import os
import tempfile
from pathlib import Path
from datetime import datetime
import pytest
from icalendar import Calendar
from dsb_converter.api import extract_ticket_info, create_ics_file
from dsb_converter.api.models import TicketInfo


class TestDSBToICS:
    """Test suite for DSB PDF to ICS converter"""

    @pytest.fixture
    def test_pdf_path(self):
        """Return the path to the test PDF"""
        return "Billet.pdf"

    @pytest.fixture
    def expected_data(self):
        """Return the expected extracted data from the test PDF"""
        return {
            'from_station': 'Aarhus H',
            'to_station': 'København H',
            'departure_date': (14, 11, 2025),
            'departure_time': (13, 15),
            'arrival_time': (16, 6),
            'train_type': 'InterCityLyn',
            'train_number': '42',
            'wagon': '91',
            'seat': '22',
            'class': '1. klasse',
            'price': '30'
        }

    def test_pdf_exists(self, test_pdf_path):
        """Test that the test PDF file exists"""
        assert Path(test_pdf_path).exists(), f"Test PDF not found: {test_pdf_path}"

    def test_extract_ticket_info(self, test_pdf_path, expected_data):
        """Test that ticket information is correctly extracted from PDF"""
        info = extract_ticket_info(test_pdf_path)

        # Verify info is a TicketInfo object
        assert isinstance(info, TicketInfo), f"Expected TicketInfo, got {type(info)}"

        # Verify all expected fields are present and correct
        assert info.from_station == expected_data['from_station']
        assert info.to_station == expected_data['to_station']
        assert info.departure_date == expected_data['departure_date']
        assert info.departure_time == expected_data['departure_time']
        assert info.arrival_time == expected_data['arrival_time']
        assert info.train_type == expected_data['train_type']
        assert info.train_number == expected_data['train_number']
        assert info.wagon == expected_data['wagon']
        assert info.seat == expected_data['seat']
        assert info.travel_class == expected_data['class']
        assert info.price == expected_data['price']

    def test_create_ics_file(self, test_pdf_path, expected_data):
        """Test that ICS file is correctly created"""
        # Extract info
        info = extract_ticket_info(test_pdf_path)

        # Create ICS in a temporary file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.ics', delete=False) as f:
            temp_ics_path = f.name

        try:
            # Create ICS file
            create_ics_file(info, temp_ics_path)

            # Verify file was created
            assert Path(temp_ics_path).exists(), "ICS file was not created"

            # Parse the ICS file
            with open(temp_ics_path, 'rb') as f:
                cal = Calendar.from_ical(f.read())

            # Get the event
            events = [component for component in cal.walk() if component.name == 'VEVENT']
            assert len(events) == 1, f"Expected 1 event, found {len(events)}"

            event = events[0]

            # Verify event fields
            assert event.get('summary') == 'DSB Rejse – Aarhus H → København H', \
                f"Wrong summary: {event.get('summary')}"

            assert event.get('location') == 'Aarhus H til København H', \
                f"Wrong location: {event.get('location')}"

            # Verify times (convert to UTC for comparison)
            dtstart = event.get('dtstart').dt
            dtend = event.get('dtend').dt

            # Expected times in UTC
            expected_start = datetime(2025, 11, 14, 12, 15, 0)  # 13:15 CET = 12:15 UTC
            expected_end = datetime(2025, 11, 14, 15, 6, 0)      # 16:06 CET = 15:06 UTC

            # Compare without timezone info (both should be in UTC)
            assert dtstart.replace(tzinfo=None) == expected_start, \
                f"Wrong start time: expected {expected_start}, got {dtstart}"
            assert dtend.replace(tzinfo=None) == expected_end, \
                f"Wrong end time: expected {expected_end}, got {dtend}"

            # Verify description contains all the details
            description = event.get('description')
            assert 'InterCityLyn 42' in description, "Missing train info in description"
            assert 'vogn 91' in description, "Missing wagon info in description"
            assert 'plads 22' in description, "Missing seat info in description"
            assert '1. klasse' in description, "Missing class info in description"
            assert 'pris 30 kr.' in description, "Missing price info in description"

            # Verify categories
            categories = event.get('categories')
            # Categories can be returned as a vCategory object, list, or string
            if hasattr(categories, 'to_ical'):
                categories_str = categories.to_ical().decode('utf-8')
            else:
                categories_str = str(categories)
            assert 'Travel' in categories_str, \
                f"Wrong categories: {categories_str}"

        finally:
            # Clean up temporary file
            if Path(temp_ics_path).exists():
                os.unlink(temp_ics_path)

    def test_end_to_end(self, test_pdf_path):
        """Test complete workflow from PDF to ICS"""
        output_path = "test_output.ics"

        try:
            # Extract info
            info = extract_ticket_info(test_pdf_path)

            # Create ICS
            create_ics_file(info, output_path)

            # Verify file exists
            assert Path(output_path).exists(), "Output ICS file not created"

            # Verify file is valid ICS
            with open(output_path, 'rb') as f:
                cal = Calendar.from_ical(f.read())
                assert cal, "Invalid ICS file"

        finally:
            # Clean up
            if Path(output_path).exists():
                os.unlink(output_path)

    def test_station_with_st_suffix(self):
        """Test extraction of stations ending in St. (like Skanderborg St.)"""
        # Check if Billet2.pdf exists
        billet2_path = "Billet2.pdf"
        if not Path(billet2_path).exists():
            pytest.skip("Billet2.pdf not found, skipping St. suffix test")

        # Extract info from Billet2.pdf
        info = extract_ticket_info(billet2_path)

        # Verify stations are correctly extracted
        assert info.from_station is not None, "Missing from_station"
        assert info.to_station is not None, "Missing to_station"

        # Should be København H → Skanderborg St.
        assert info.from_station == 'København H', \
            f"Expected 'København H', got '{info.from_station}'"
        assert 'Skanderborg' in info.to_station, \
            f"Expected station with 'Skanderborg', got '{info.to_station}'"

        # Create ICS and verify
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.ics', delete=False) as f:
            temp_ics_path = f.name

        try:
            create_ics_file(info, temp_ics_path)

            # Parse and verify
            with open(temp_ics_path, 'rb') as f:
                cal = Calendar.from_ical(f.read())

            events = [component for component in cal.walk() if component.name == 'VEVENT']
            assert len(events) == 1

            event = events[0]
            summary = event.get('summary')
            assert 'Skanderborg' in summary, \
                f"Expected 'Skanderborg' in summary, got '{summary}'"

        finally:
            if Path(temp_ics_path).exists():
                os.unlink(temp_ics_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
