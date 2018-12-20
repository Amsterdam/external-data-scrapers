from data_sources.parkeergarages.models import (GuidanceSign, GuidanceSignRaw,
                                                ParkingLocation,
                                                ParkingLocationRaw)

PARKING_LOCATION_URL = 'http://opd.it-t.nl/data/amsterdam/ParkingLocation.json'
GUIDANCE_SIGN_URL = 'http://opd.it-t.nl/data/amsterdam/GuidanceSign.json'

ENDPOINTS = [
    'parking_location',
    'guidance_sign'
]

ENDPOINT_URL = {
    'parking_location': PARKING_LOCATION_URL,
    'guidance_sign': GUIDANCE_SIGN_URL
}

ENDPOINT_MODEL = {
    'parking_location': ParkingLocation,
    'guidance_sign': GuidanceSign,
}

ENDPOINT_RAW_MODEL = {
    'parking_location': ParkingLocationRaw,
    'guidance_sign': GuidanceSignRaw,
}
