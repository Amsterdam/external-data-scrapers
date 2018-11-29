import argparse
import asyncio
import logging

from sqlalchemy import TIMESTAMP, Column, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Sequence

# from aiopg.sa import create_engine as aiopg_engine
import db_helper

# logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

Base = declarative_base()


async def main(args):
    """Main."""
    engine = db_helper.make_engine(section="docker")

    if args.drop:
        # resets everything
        LOG.warning("DROPPING ALL DEFINED TABLES")
        Base.metadata.drop_all(engine)

    LOG.warning("CREATING DEFINED TABLES")
    # recreate tables
    Base.metadata.create_all(engine)


class OvFiets(Base):
    """Raw Enevo ServiceEvent data."""
    __tablename__ = f"ovfiets_raw"
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
