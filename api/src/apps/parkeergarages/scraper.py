from apps.base.base_api_scraper import BaseAPIScraper
from apps.parkeergarages.models import (GuidanceSignSnapshot,
                                        ParkingLocationSnapshot)


class ParkingLocationScraper(BaseAPIScraper):
    url = 'http://opd.it-t.nl/data/amsterdam/ParkingLocation.json'
    model = ParkingLocationSnapshot


class GuidanceSignScraper(BaseAPIScraper):
    url = 'http://opd.it-t.nl/data/amsterdam/GuidanceSign.json'
    model = GuidanceSignSnapshot
