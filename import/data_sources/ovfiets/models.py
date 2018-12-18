import argparse
import asyncio
import logging

from geoalchemy2 import Geometry
from sqlalchemy import TIMESTAMP, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Sequence

# from aiopg.sa import create_engine as aiopg_engine
import db_helper

# logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

Base = declarative_base()

OVFIETS_TABLES = [
    # should never be dropped
    # "ovfiets_raw",
    "importer_ovfiets",
]


async def main(args):
    """Main."""
    engine = db_helper.make_engine(section="docker")

    session = db_helper.set_session(engine)

    if args.drop:
        # resets everything
        LOG.warning("DROPPING ALL DEFINED TABLES")
        for table in OVFIETS_TABLES:
            session.execute(f"DROP table if exists {table};")
        session.commit()

    LOG.warning("CREATING DEFINED TABLES")
    # recreate tables
    Base.metadata.create_all(engine)


class OvFietsRaw(Base):
    """Raw OvFiets data."""
    __tablename__ = f"ovfiets_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class OvFiets(Base):
    """Cleaned up OVFiets data."""
    __tablename__ = f"importer_ovfiets"

    id = Column(Integer, Sequence("grl_seq"), primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    station_code = Column(String)
    location_code = Column(String, index=True)
    open = Column(String)
    geometrie = Column(Geometry('POINT', srid=4326), index=True)
    fetch_time = Column(TIMESTAMP, index=True)
    rental_bikes = Column(Integer, index=True)
    scraped_at = Column(TIMESTAMP, index=True)
    opening_hours = Column(JSONB)
    stadsdeel = Column(String, index=True)
    unmapped = Column(JSONB)


if __name__ == "__main__":
    desc = "Create/Drop defined model tables."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--drop", action="store_true", default=False, help="Drop existing"
    )

    args = inputparser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
