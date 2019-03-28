import argparse
import asyncio
import logging

from sqlalchemy import (TIMESTAMP, BigInteger, Column, ForeignKey, Integer,
                        String)
from sqlalchemy.ext.declarative import declarative_base

import db_helper

LOG = logging.getLogger(__name__)

Base = declarative_base()

WIFIINFO_TABLES = [
    # NEVER drop raw models
    "importer_wifiinfo"
]


async def main(args):
    """Main."""
    engine = db_helper.make_engine(section="docker")

    session = db_helper.set_session(engine)

    if args.drop:
        # resets everything
        LOG.warning("DROPPING ALL DEFINED TABLES")
        for table in WIFIINFO_TABLES:
            session.execute(f"DROP table if exists {table};")
        session.commit()

    LOG.warning("CREATING DEFINED TABLES")
    # recreate tables
    Base.metadata.create_all(engine)


class WifiInfoFields:
    id = Column(Integer, primary_key=True, index=True, autoincrement='auto')
    unique_id = Column(BigInteger)
    sensor = Column(String)
    first_detection = Column(TIMESTAMP)
    last_detection = Column(TIMESTAMP)
    strongest_signal_timestamp = Column(TIMESTAMP)
    strongest_signal_rssi = Column(Integer)
    report_name = Column(String(length=255))


class CSVFileInfo(Base):
    """CSVFileInfo data."""
    __tablename__ = f"csvfileinfo"
    csv_name = Column(String, primary_key=True, unique=True)
    scraped_at = Column(TIMESTAMP, index=True)


class TempWifiInfo(WifiInfoFields, Base):
    """Temp WifiInfo data."""
    __tablename__ = f"temp_importer_wifiinfo"


class WifiInfo(WifiInfoFields, Base):
    """Cleaned up WifiInfo data."""
    __tablename__ = f"importer_wifiinfo"
    csv_name = Column(String, ForeignKey(CSVFileInfo.csv_name))


if __name__ == "__main__":
    desc = "Create/Drop defined model tables."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--drop", action="store_true", default=False, help="Drop existing"
    )

    args = inputparser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
