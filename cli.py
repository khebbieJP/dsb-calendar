#!/usr/bin/env python3
"""
CLI tool for converting DSB ticket PDFs to ICS calendar files
"""

import sys
import logging
from pathlib import Path

from dsb_converter.api import extract_ticket_info, create_ics_file
from dsb_converter.api.parsers import TicketParsingError
from dsb_converter.api.calendar import CalendarGenerationError


def setup_cli_logging():
    """Configure logging for CLI use with human-readable output"""
    logger = logging.getLogger('dsb_cli')
    logger.setLevel(logging.INFO)

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler with simple format for CLI
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # Use simple formatter for human-readable CLI output
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False

    return logger


def print_usage(logger):
    """Print usage information"""
    logger.info("Usage: python cli.py <input_pdf> [output_ics]")
    logger.info("Example: python cli.py Billet.pdf DSB_Rejse_2025-11-14.ics")


def main():
    """Main CLI function"""
    logger = setup_cli_logging()

    if len(sys.argv) < 2:
        print_usage(logger)
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
        logger.error(f"Error: File '{input_pdf}' not found.")
        sys.exit(1)

    logger.info(f"Processing: {input_pdf}")

    # Extract information from PDF
    try:
        info = extract_ticket_info(input_pdf)

        # Display extracted information
        logger.info("\nExtracted Information:")
        logger.info(f"  From: {info.from_station or 'N/A'}")
        logger.info(f"  To: {info.to_station or 'N/A'}")

        if info.departure_date:
            logger.info(f"  Departure: {info.get_formatted_departure()}")

        if info.arrival_time:
            logger.info(f"  Arrival: {info.get_formatted_arrival()}")

        if info.train_type and info.train_number:
            logger.info(f"  Train: {info.train_type} {info.train_number}")

        if info.wagon:
            logger.info(f"  Wagon: {info.wagon}")

        if info.seat:
            logger.info(f"  Seat: {info.seat}")

        if info.travel_class:
            logger.info(f"  Class: {info.travel_class}")

        if info.price:
            logger.info(f"  Price: {info.price} kr.")

        # Validate extracted information
        if not info.is_valid():
            logger.warning("\nWarning: Some required information is missing.")
            logger.warning("The ICS file may not be complete.")

        # Create ICS file
        logger.info(f"\nCreating ICS file...")
        create_ics_file(info, output_ics)

        logger.info(f"ICS file created: {output_ics}")
        logger.info("\nDone!")

    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

    except TicketParsingError as e:
        logger.error(f"Error parsing PDF: {e}", exc_info=True)
        sys.exit(1)

    except CalendarGenerationError as e:
        logger.error(f"Error creating calendar: {e}")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
