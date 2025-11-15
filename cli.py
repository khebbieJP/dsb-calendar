#!/usr/bin/env python3
"""
CLI tool for converting DSB ticket PDFs to ICS calendar files
"""

import sys
from pathlib import Path

from dsb_converter.api import extract_ticket_info, create_ics_file
from dsb_converter.api.parsers import TicketParsingError
from dsb_converter.api.calendar import CalendarGenerationError


def print_usage():
    """Print usage information"""
    print("Usage: python cli.py <input_pdf> [output_ics]")
    print("Example: python cli.py Billet.pdf DSB_Rejse_2025-11-14.ics")


def main():
    """Main CLI function"""
    if len(sys.argv) < 2:
        print_usage()
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
        print(f"  From: {info.from_station or 'N/A'}")
        print(f"  To: {info.to_station or 'N/A'}")

        if info.departure_date:
            print(f"  Departure: {info.get_formatted_departure()}")

        if info.arrival_time:
            print(f"  Arrival: {info.get_formatted_arrival()}")

        if info.train_type and info.train_number:
            print(f"  Train: {info.train_type} {info.train_number}")

        if info.wagon:
            print(f"  Wagon: {info.wagon}")

        if info.seat:
            print(f"  Seat: {info.seat}")

        if info.travel_class:
            print(f"  Class: {info.travel_class}")

        if info.price:
            print(f"  Price: {info.price} kr.")

        # Validate extracted information
        if not info.is_valid():
            print("\nWarning: Some required information is missing.")
            print("The ICS file may not be complete.")

        # Create ICS file
        print(f"\nCreating ICS file...")
        create_ics_file(info, output_ics)

        print(f"ICS file created: {output_ics}")
        print("\nDone!")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    except TicketParsingError as e:
        print(f"Error parsing PDF: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    except CalendarGenerationError as e:
        print(f"Error creating calendar: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
