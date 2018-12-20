import argparse
import logging
import time

import db_helper
import settings
from data_sources.latest_query import get_latest_query
from data_sources.link_areas import link_areas
from data_sources.parkeergarages.endpoints import (ENDPOINT_MODEL,
                                                   ENDPOINT_RAW_MODEL,
                                                   ENDPOINTS)
from data_sources.parkeergarages.models import (ParkingGuidanceDisplay,
                                                ParkingLocation)

log = logging.getLogger(__name__)


def store_guidance_sign(raw_data):
    session = db_helper.session
    gsign = {}
    pg_displ_list = []

    for instance in raw_data:
        for feature in instance.data['features']:
            lng = feature['geometry']['coordinates'][0]
            lat = feature['geometry']['coordinates'][1]
            props = feature['properties']
            gs_api_id = feature['Id']

            # Order is important for the query
            guidance_sign = (
                gs_api_id,
                f'SRID=4326;POINT({lng} {lat})',
                props.get('Name'),
                props.get('Type'),
                props.get('State'),
                props.get('PubDate'),
                props.get('Removed'),
                str(instance.scraped_at),
            )

            gsign[gs_api_id] = str(guidance_sign)

            for display in props['ParkingguidanceDisplay']:
                pgd = dict(
                    api_id=display.get('Id'),
                    pub_date=props.get('PubDate'),
                    description=display.get('Description'),
                    type=display.get('Type'),
                    output=display.get('Output'),
                    output_description=display.get('OutputDescription'),
                    guidance_sign_id=gs_api_id,
                    scraped_at=instance.scraped_at,

                )
                pg_displ_list.append(pgd)

    log.info(
        "Insertins/Updating {} GuidanceSign entries".format(len(gsign))
    )

    session.execute(INSERT_GUIDANCE_SIGN.format(', '.join(gsign.values())))

    log.info(
        "Creating {} ParkingGuidanceDisplay entries".format(len(pg_displ_list))
    )
    session.bulk_insert_mappings(
        ParkingGuidanceDisplay, pg_displ_list
    )
    session.commit()


def store_parking_location(raw_data):
    session = db_helper.session

    parking_locations = []
    for instance in raw_data:
        for feature in instance.data['features']:
            lng = feature['geometry']['coordinates'][0]
            lat = feature['geometry']['coordinates'][1]
            props = feature['properties']
            free_sp_s = props.get('FreeSpaceShort')
            free_sp_l = props.get('FreeSpaceLong')
            s_capacity = props.get('ShortCapacity')
            l_capacity = props.get('LongCapacity')

            parking_location = dict(
                api_id=feature.get('Id'),
                scraped_at=instance.scraped_at,
                name=props.get('Name', None),
                type=props.get('Type', None),
                geometrie=f'SRID=4326;POINT({lng} {lat})',
                state=props.get('State'),
                free_space_short=int(free_sp_s) if free_sp_s else 0,
                free_space_long=int(free_sp_l) if free_sp_l else 0,
                short_capacity=int(s_capacity) if s_capacity else 0,
                long_capacity=int(l_capacity) if l_capacity else 0,
                pub_date=props.get('PubDate'),
            )

            parking_locations.append(parking_location)

    log.info(
        "Storing {} ParkingLocation entries".format(len(parking_locations))
    )
    session.bulk_insert_mappings(ParkingLocation, parking_locations)
    session.commit()


def start_import(store_func, raw_model, clean_model):
    """
    Importing the data is done in batches to avoid
    straining the resources.
    """
    session = db_helper.session
    query = get_latest_query(session, raw_model, clean_model)
    run = True

    offset = 0
    limit = settings.DATABASE_IMPORT_LIMIT

    while run:
        raw_data = query.offset(offset).limit(limit).all()

        if raw_data:
            log.info("Current offset {}".format(offset))
            log.info(
                "Fetched {} raw entries".format(len(raw_data))
            )
            store_func(raw_data)
            offset += limit
        else:
            run = False


ENDPOINTS_STORE_FUNC = {
    'parking_location': store_parking_location,
    'guidance_sign': store_guidance_sign,
}

INSERT_GUIDANCE_SIGN = """
INSERT INTO importer_guidancesign (
api_id, geometrie, name, type, state, pub_date, removed, scraped_at
)
VALUES {}
ON CONFLICT (api_id) DO UPDATE
  SET geometrie = excluded.geometrie,
      name = excluded.name,
      type = excluded.type,
      state = excluded.state,
      pub_date = excluded.pub_date,
      removed = excluded.removed,
      scraped_at = excluded.scraped_at;
"""


def main(make_engine=True):
    desc = "Clean data and import into db."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "endpoint",
        type=str,
        default="parking_location",
        choices=ENDPOINTS,
        help="Provide Endpoint to scrape",
        nargs=1,
    )

    inputparser.add_argument(
        "--link_areas", action="store_true",
        default=False, help="Link stations with neighbourhood areas"
    )

    args = inputparser.parse_args()

    start = time.time()

    if make_engine:
        engine = db_helper.make_engine()
        db_helper.set_session(engine)

    session = db_helper.session

    endpoint = args.endpoint[0]
    raw_model = ENDPOINT_RAW_MODEL[endpoint]
    clean_model = ENDPOINT_MODEL[endpoint]
    store_func = ENDPOINTS_STORE_FUNC[endpoint]

    if args.link_areas:
        link_areas(session, clean_model.__tablename__)
    else:
        start_import(
            store_func,
            raw_model,
            clean_model
        )

    log.info("Took: %s", time.time() - start)
    session.close()


if __name__ == "__main__":
    main()
