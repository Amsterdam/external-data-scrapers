import argparse
import asyncio
import logging

from geoalchemy2 import Geometry
from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Sequence

import db_helper

LOG = logging.getLogger(__name__)

Base = declarative_base()

PARKEERGARAGES_TABLES = [
    # NEVER drop raw models
    "importer_parkinglocation",
    "importer_parkingguidancedisplay",
    "importer_guidancesign",
]


async def main(args):
    """Main."""
    engine = db_helper.make_engine(section="docker")

    session = db_helper.set_session(engine)

    if args.drop:
        # resets everything
        LOG.warning("DROPPING ALL DEFINED TABLES")
        for table in PARKEERGARAGES_TABLES:
            session.execute(f"DROP table if exists {table};")
        session.commit()

    LOG.warning("CREATING DEFINED TABLES")
    # recreate tables
    Base.metadata.create_all(engine)


class ParkingLocationRaw(Base):
    """Raw parking location data."""
    __tablename__ = f"parkinglocation_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class ParkingLocation(Base):
    __tablename__ = f"importer_parkinglocation"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True, index=True)
    api_id = Column(String, index=True)
    name = Column(String, index=True)
    type = Column(String, index=True)
    geometrie = Column(Geometry('POINT', srid=4326), index=True)
    state = Column(String, index=True)
    free_space_short = Column(Integer, index=True)
    free_space_long = Column(Integer, index=True)
    short_capacity = Column(Integer, index=True)
    long_capacity = Column(Integer, index=True)
    pub_date = Column(TIMESTAMP, index=True)
    stadsdeel = Column(String, index=True)
    buurt_code = Column(String, index=True)
    scraped_at = Column(TIMESTAMP, index=True)


class GuidanceSign(Base):
    __tablename__ = f"importer_guidancesign"
    id = Column(Integer, primary_key=True, index=True, autoincrement='auto')
    api_id = Column(String, index=True, unique=True)
    geometrie = Column(Geometry('POINT', srid=4326), index=True)
    name = Column(String, index=True)
    type = Column(String, index=True)
    state = Column(String, index=True)
    pub_date = Column(TIMESTAMP, index=True)
    removed = Column(Boolean, index=True)
    stadsdeel = Column(String, index=True)
    buurt_code = Column(String, index=True)
    scraped_at = Column(TIMESTAMP, index=True)


class ParkingGuidanceDisplay(Base):
    __tablename__ = f"importer_parkingguidancedisplay"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True, index=True)
    api_id = Column(String, index=True)
    pub_date = Column(TIMESTAMP, index=True)
    description = Column(String)
    type = Column(String, index=True)
    output = Column(String, index=True)
    output_description = Column(String, index=True)
    guidance_sign_id = Column(String, ForeignKey(GuidanceSign.api_id))
    scraped_at = Column(TIMESTAMP, index=True)


class GuidanceSignRaw(Base):
    """Raw guidance sign data."""
    __tablename__ = f"guidancesign_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


if __name__ == "__main__":
    desc = "Create/Drop defined model tables."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--drop", action="store_true", default=False, help="Drop existing"
    )

    args = inputparser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
