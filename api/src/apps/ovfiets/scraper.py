from apps.base.base_api_scraper import BaseAPIScraper
from apps.ovfiets.models import OvFietsRaw


class OvFietsScraper(BaseAPIScraper):
    url = 'http://fiets.openov.nl/locaties.json'
    model = OvFietsRaw
