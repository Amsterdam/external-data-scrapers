import argparse
import asyncio
import logging

from sqlalchemy import TIMESTAMP, Column, Integer
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


if __name__ == "__main__":
    desc = "Create/Drop defined model tables."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--drop", action="store_true", default=False, help="Drop existing"
    )

    args = inputparser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
