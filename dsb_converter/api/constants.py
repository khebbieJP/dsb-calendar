"""
Constants for DSB ticket conversion
"""

# Danish month abbreviations to month numbers
DANISH_MONTHS = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
    'maj': 5, 'jun': 6, 'jul': 7, 'aug': 8,
    'sep': 9, 'okt': 10, 'nov': 11, 'dec': 12
}

# Common Danish station name suffixes
STATION_SUFFIXES = ['H', 'St.', 'M']

# DSB train types
TRAIN_TYPES = ['InterCityLyn', 'InterCity', 'Regionaltog', 'Lyn']

# Travel class identifiers
TRAVEL_CLASS_PATTERNS = ['DSB 1\'', 'DSB 2\'', '1. klasse', '2. klasse']
TRAVEL_CLASS_FIRST = '1. klasse'
TRAVEL_CLASS_SECOND = '2. klasse'

# ICS calendar configuration
CALENDAR_PRODUCT_ID = '-//DSB Transport//example.com//'
CALENDAR_VERSION = '2.0'
CALENDAR_EVENT_CATEGORY = 'Travel'

# File upload constraints
MAX_FILE_SIZE_MB = 16
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {'pdf'}

# Timezone
COPENHAGEN_TIMEZONE = 'Europe/Copenhagen'
