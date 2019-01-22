import argparse
import asyncio
import logging

from geoalchemy2 import Geometry
from sqlalchemy import TIMESTAMP, Boolean, Column, Float, Integer, String
from sqlalchemy.dialects.postgresql import BYTEA, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Sequence

# from aiopg.sa import create_engine as aiopg_engine
import db_helper

# logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

Base = declarative_base()

NDW_TABLES = [
    # should never be dropped
    # "traveltime_raw",
    # "thirdparty_traveltime_raw",
    "importer_traveltime",
    "importer_thirdparty_traveltime",
]


async def main(args):
    """Main."""
    engine = db_helper.make_engine(section="docker")

    session = db_helper.set_session(engine)

    if args.drop:
        # resets everything
        LOG.warning("DROPPING ALL DEFINED TABLES")
        for table in NDW_TABLES:
            session.execute(f"DROP table if exists {table};")
        session.commit()

    LOG.warning("CREATING DEFINED TABLES")
    # recreate tables
    Base.metadata.create_all(engine)


class ThirdpartyTravelTimeRaw(Base):
    """Raw TravelTime data."""
    __tablename__ = f"thirdparty_traveltime_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class TravelTimeRaw(Base):
    """Raw TravelTime data."""
    __tablename__ = f"traveltime_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(BYTEA)


class ThirdpartyTravelTime(Base):
    """Cleaned up TravelTime data."""
    __tablename__ = f"importer_thirdparty_traveltime"
    id = Column(Integer, primary_key=True, index=True, autoincrement='auto')
    measurement_site_reference = Column(String)
    name = Column(String(255))
    type = Column(String(length=2))
    length = Column(Integer)
    geometrie = Column(Geometry('LineString', srid=4326))
    traveltime = Column(Integer, nullable=True)
    velocity = Column(Integer, nullable=True)
    timestamp = Column(TIMESTAMP, index=True)
    scraped_at = Column(TIMESTAMP, index=True)


class TravelTime(Base):
    """Imported xml data from ndw datasource"""
    __tablename__ = f"importer_traveltime"
    id = Column(Integer, primary_key=True, index=True, autoincrement='auto')
    measurement_site_reference = Column(String(length=255), index=True)

    computational_method = Column(String(length=255), nullable=True)
    number_of_incomplete_input = Column(Integer)
    number_of_input_values_used = Column(Integer)
    standard_deviation = Column(Float)
    supplier_calculated_data_quality = Column(Float)
    duration = Column(Float)
    data_error = Column(Boolean)
    measurement_time = Column(TIMESTAMP, index=True)
    scraped_at = Column(TIMESTAMP, index=True)


if __name__ == "__main__":
    desc = "Create/Drop defined model tables."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--drop", action="store_true", default=False, help="Drop existing"
    )

    args = inputparser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
