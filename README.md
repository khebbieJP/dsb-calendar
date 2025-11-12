# DSB Ticket PDF to ICS Calendar Converter

A Python tool that extracts train journey information from Danish State Railways (DSB) ticket PDFs and generates ICS calendar files for easy import into calendar applications.

## Features

- Extracts journey details from DSB Print Selv-billet PDFs
- Generates standard ICS (iCalendar) files compatible with all major calendar applications
- Correctly handles Danish date/time formats and station names
- Includes comprehensive journey details (train number, wagon, seat, class, price)
- Automatic timezone conversion (Copenhagen time to UTC)

## Installation

1. Ensure Python 3.11+ is installed and configured with mise:

```bash
mise trust
mise install
```

2. Install dependencies:

```bash
mise exec -- uv pip install -r requirements.txt
```

## Usage

### Using Mise Tasks (Recommended)

The project includes convenient mise tasks for common operations:

```bash
# View all available tasks
mise tasks

# Install dependencies
mise run install

# Run tests
mise run test

# Convert a PDF to ICS
mise run convert -- Billet.pdf DSB_Rejse_2025-11-14.ics

# Run example conversion
mise run example

# Clean up generated files
mise run clean
```

### Direct Python Usage

You can also run the script directly:

```bash
mise exec -- python dsb_to_ics.py Billet.pdf DSB_Rejse_2025-11-14.ics
```

If you don't specify an output filename, it will use the input filename with `.ics` extension:

```bash
mise exec -- python dsb_to_ics.py Billet.pdf
# Creates: Billet.ics
```

### Example Output

The script will display extracted information:

```
Processing: Billet.pdf

Extracted Information:
  From: Aarhus H
  To: København H
  Departure: 2025-11-14 13:15
  Arrival: 16:06
  Train: InterCityLyn 42
  Wagon: 91
  Seat: 22
  Class: 1. klasse
  Price: 30 kr.

Creating ICS file...
ICS file created: DSB_Rejse_2025-11-14.ics

Done!
```

## Testing

Run the automated test suite:

```bash
# Using mise task (recommended)
mise run test

# Or directly
mise exec -- pytest test_dsb_to_ics.py -v
```

The test suite verifies:
- PDF file reading and parsing
- Correct extraction of all journey details
- Valid ICS file generation
- Proper timezone conversion
- Complete end-to-end workflow

## Extracted Information

The tool extracts the following information from DSB tickets:

- **Departure station** (e.g., "Aarhus H")
- **Arrival station** (e.g., "København H")
- **Departure date and time**
- **Arrival time**
- **Train type and number** (e.g., "InterCityLyn 42")
- **Wagon number**
- **Seat number**
- **Travel class** (1st or 2nd class)
- **Ticket price**

## Generated ICS File Format

The generated ICS file includes:

- **Event summary**: "DSB Rejse – [From] → [To]"
- **Location**: "[From] til [To]"
- **Start/End times**: Correctly converted to UTC
- **Description**: Train details, wagon, seat, class, and price
- **Category**: Travel

## Requirements

- Python 3.11+
- pdfplumber 0.11.0 (for PDF parsing)
- icalendar 5.0.11 (for ICS generation)
- python-dateutil 2.8.2 (for timezone handling)
- pytest 8.0.0 (for testing)

## Available Mise Tasks

The project includes the following convenient tasks:

| Task | Description |
|------|-------------|
| `mise run install` | Install Python dependencies |
| `mise run test` | Run automated tests |
| `mise run convert -- <input.pdf> [output.ics]` | Convert a DSB ticket PDF to ICS (note the `--`) |
| `mise run example` | Run example conversion with Billet.pdf |
| `mise run clean` | Clean up generated files and cache |

View all tasks:
```bash
mise tasks
```

## Project Structure

```
.
├── .mise.toml              # Mise configuration with tasks
├── .tool-versions          # Tool versions
├── requirements.txt        # Python dependencies
├── dsb_to_ics.py          # Main converter script
├── test_dsb_to_ics.py     # Automated tests
├── Billet.pdf             # Example DSB ticket
└── README.md              # This file
```

## Supported Ticket Types

Currently tested with:
- DSB Print Selv-billet (Print-at-home tickets)
- InterCityLyn trains
- InterCity trains
- Regional trains

## Supported Stations

The tool recognizes Danish stations with common suffixes:
- **H** - Hovedbanegård (e.g., København H, Aarhus H)
- **St.** - Station (e.g., Skanderborg St., Fredericia St.)
- **M** - Other stations (e.g., Odense M)

Tested with routes including:
- Aarhus H ↔ København H
- København H ↔ Skanderborg St.

## Limitations

- Requires valid DSB ticket PDFs with standard format
- Year is inferred from booking date or current date if month has passed
- Best results with standard DSB Print Selv-billet format

## Contributing

To add support for additional ticket formats or stations:

1. Add test PDF samples
2. Update the regex patterns in `extract_ticket_info()`
3. Add corresponding test cases in `test_dsb_to_ics.py`
4. Run the test suite to verify

## License

This is a personal utility tool. Use at your own discretion.
