# DSB Ticket PDF to ICS Converter

A Python application for converting Danish State Railways (DSB) ticket PDFs into ICS calendar files. Features a clean API, Flask web application, and command-line interface.

## Features

- **Clean API Architecture**: Modular design with parsers, calendar generation, and data models
- **Flask Web Application**: User-friendly web interface with drag-and-drop file upload
- **REST API**: JSON endpoints for programmatic access
- **CLI Tool**: Command-line interface for batch processing
- **Docker Support**: Easy deployment with Docker and docker-compose
- **Comprehensive Testing**: Full test suite with pytest
- **Error Handling**: Robust validation and error messages

## Quick Start

### Web Interface

```bash
mise run web
# Open http://localhost:5000
```

### Command Line

```bash
mise run convert -- Billet.pdf output.ics
```

### Docker

```bash
docker-compose up --build
# Open http://localhost:5000
```

## Installation

1. Ensure mise is installed and Python 3.11+ is configured:

```bash
mise trust
mise install
```

2. Install dependencies:

```bash
mise run install
```

## Usage

### Web Application

Start the Flask server:

```bash
# Production mode
mise run web

# Development mode (with debug enabled)
mise run dev
```

The web interface supports:
- Drag-and-drop file upload
- JSON response for viewing extracted data
- ICS file download for calendar import
- Real-time validation and error messages

### REST API

**Health Check:**
```bash
curl http://localhost:5000/api/health
```

**Convert PDF to ICS:**
```bash
curl -X POST -F "file=@Billet.pdf" \
  http://localhost:5000/api/convert \
  -o ticket.ics
```

**Get JSON Data:**
```bash
curl -X POST -F "file=@Billet.pdf" -F "format=json" \
  http://localhost:5000/api/convert
```

### Command Line Interface

```bash
# Basic usage
mise run convert -- Billet.pdf

# Specify output filename
mise run convert -- Billet.pdf my_journey.ics

# Run example
mise run example
```

### Python API

```python
from dsb_converter.api import extract_ticket_info, create_ics_file

# Extract ticket information
info = extract_ticket_info("Billet.pdf")

# Validate and create ICS file
if info.is_valid():
    create_ics_file(info, "output.ics")

# Access ticket data
print(f"Route: {info.from_station} → {info.to_station}")
print(f"Departure: {info.get_formatted_departure()}")
```

## Project Structure

```
.
├── dsb_converter/              # Main package
│   └── api/                    # Core API modules
│       ├── models.py          # Data models (TicketInfo)
│       ├── parsers.py         # PDF parsing logic
│       ├── calendar.py        # ICS generation
│       └── utils.py           # Utility functions
├── templates/                  # Flask HTML templates
│   └── index.html
├── static/                     # Static assets
├── app.py                     # Flask web application
├── cli.py                     # Command-line interface
├── test_api.py                # Flask API tests
├── test_dsb_to_ics.py        # Core functionality tests
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
└── docker-compose.yml         # Docker Compose setup
```

## API Reference

### TicketInfo Model

```python
from dsb_converter.api.models import TicketInfo

# Attributes
info.from_station: str
info.to_station: str
info.departure_date: tuple[int, int, int]  # (day, month, year)
info.departure_time: tuple[int, int]       # (hour, minute)
info.arrival_time: tuple[int, int]         # (hour, minute)
info.train_type: str
info.train_number: str
info.wagon: str
info.seat: str
info.travel_class: str
info.price: str

# Methods
info.is_valid() -> bool
info.to_dict() -> dict
info.get_formatted_departure() -> str
info.get_formatted_arrival() -> str
```

### Functions

**extract_ticket_info(pdf_path) -> TicketInfo**
- Extract journey information from DSB ticket PDF
- Raises: `FileNotFoundError`, `TicketParsingError`

**create_ics_file(info, output_path) -> None**
- Create ICS calendar file from ticket information
- Raises: `CalendarGenerationError`

**create_ics_bytes(info) -> bytes**
- Create ICS calendar data as bytes
- Raises: `CalendarGenerationError`

## Testing

Run the test suite:

```bash
mise run test
```

The test suite includes:
- **API Tests** (`test_api.py`) - Flask endpoints, health checks, file uploads, error handling
- **Core Tests** (`test_dsb_to_ics.py`) - PDF parsing, ICS generation, data extraction

All tests verify outer interfaces, not implementation details.

## Available Mise Tasks

| Task | Description |
|------|-------------|
| `mise run install` | Install Python dependencies |
| `mise run test` | Run automated tests |
| `mise run web` | Start Flask web application |
| `mise run dev` | Start Flask in debug mode |
| `mise run convert -- <pdf> [ics]` | Convert PDF to ICS |
| `mise run example` | Run example conversion |
| `mise run clean` | Clean generated files |

## Configuration

### Environment Variables

- `FLASK_DEBUG` - Enable debug mode (default: `false`)
- `FLASK_HOST` - Server host (default: `0.0.0.0`)
- `FLASK_PORT` - Server port (default: `5000`)

Example:
```bash
export FLASK_PORT=8000
python app.py
```

## Docker Deployment

### Production

```bash
docker-compose up --build
```

### Custom Configuration

```yaml
services:
  web:
    environment:
      - FLASK_DEBUG=false
      - FLASK_PORT=5000
    ports:
      - "80:5000"
```

## Supported Features

### Ticket Types
- DSB Print Selv-billet (Print-at-home tickets)
- InterCityLyn trains
- InterCity trains
- Regional trains

### Station Types
- **H** - Hovedbanegård (e.g., København H, Aarhus H)
- **St.** - Station (e.g., Skanderborg St.)
- **M** - Other stations (e.g., Odense M)

## Dependencies

- Python 3.11+
- pdfplumber 0.11.0
- icalendar 5.0.11
- python-dateutil 2.8.2
- flask 3.0.0
- werkzeug 3.0.1
- requests 2.31.0
- pytest 8.0.0

## License

This is a personal utility tool. Use at your own discretion.
