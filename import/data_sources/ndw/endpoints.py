TRAFFICSPEED_URL = 'http://opendata.ndw.nu/trafficspeed.xml.gz'
TRAVELTIME_URL = 'http://opendata.ndw.nu/traveltime.xml.gz'

SHAPEFILE_URL = (
    'http://opendata.ndw.nu/044.1_Levering_NDW_Shapefiles_20180925.zip'
)

ENDPOINTS = [
    'traveltime',
    'trafficspeed'
]

ENDPOINT_URL = {
    'traveltime': TRAVELTIME_URL,
    'trafficspeed': TRAFFICSPEED_URL
}
