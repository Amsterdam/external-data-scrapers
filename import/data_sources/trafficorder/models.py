import argparse
import asyncio
import logging

from geoalchemy2 import Geometry
from sqlalchemy import TIMESTAMP, Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.ext.declarative import declarative_base

import db_helper

LOG = logging.getLogger(__name__)

Base = declarative_base()

TRAFFICORDER_TABLES = [
    # NEVER drop raw models
    # "trafficorder_raw",
    "importer_trafficorder"
]


async def main(args):
    """Main."""
    engine = db_helper.make_engine(section="docker")

    session = db_helper.set_session(engine)

    if args.drop:
        # resets everything
        LOG.warning("DROPPING ALL DEFINED TABLES")
        for table in TRAFFICORDER_TABLES:
            session.execute(f"DROP table if exists {table};")
        session.commit()

    LOG.warning("CREATING DEFINED TABLES")
    # recreate tables
    Base.metadata.create_all(engine)


class TrafficOrderRaw(Base):
    """Raw guidance sign data."""
    __tablename__ = f"trafficorder_raw"
    id = Column(Integer, primary_key=True, index=True, autoincrement='auto')
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(BYTEA)
    part = Column(Integer)
    month = Column(Integer, nullable=True)
    year = Column(Integer)


class TrafficOrder(Base):
    """Cleaned up Trafficorder data."""
    __tablename__ = f"importer_trafficorder"
    id = Column(Integer, primary_key=True, index=True, autoincrement='auto')
    scraped_at = Column(TIMESTAMP, index=True)

    available = Column(TIMESTAMP)
    year = Column(Integer)
    creator = Column(String(length=255))
    identifier = Column(String(length=255))
    title = Column(Text)
    alternative = Column(Text)
    spatial_coordinates = Column(String(length=100))

    geometrie = Column(Geometry('Point', srid=28992))
    postcode = Column(String(length=50))
    street_name = Column(String(length=100))
    traffic_sign_code = Column(String(length=10))

    stadsdeel = Column(String, index=True)
    buurt_code = Column(String, index=True)


if __name__ == "__main__":
    desc = "Create/Drop defined model tables."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--drop", action="store_true", default=False, help="Drop existing"
    )

    args = inputparser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
