OVFIETS_RAW_TO_MODEL_MAPPING = {
    'openingHours': 'opening_hours',
    'locationCode': 'location_code',
    'stationCode': 'station_code',
    'fetchTime': 'fetch_time',
    'rentalBikes': 'rental_bikes'
}

OVFIETS_FORM_FIELDS = (
    list(OVFIETS_RAW_TO_MODEL_MAPPING.values()) + ['name', 'description', 'geometrie', 'open', 'unmapped']
)
