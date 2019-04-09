"""
We use the objectstore to get the latest and greatest of
database dump

EXAXMPLE:
---------

    assert os.getenv('HANDELSREGISTER_OBJECTSTORE_PASSWORD')

    ENV = os.getenv('ENVIRONMENT', 'ACCEPTANCE')
    OBJECTSTORE_LOCAL = os.getenv('OBJECTSTORE_LOCAL', '')

    OBJECTSTORE = dict(
        VERSION='2.0',
        AUTHURL='https://identity.stack.cloudvps.com/v2.0',
        TENANT_NAME='BGE000081_Handelsregister',
        TENANT_ID='0efc828b88584759893253f563b35f9b',
        USER=os.getenv('OBJECTSTORE_USER', 'handelsregister'),
        PASSWORD=os.getenv('HANDELSREGISTER_OBJECTSTORE_PASSWORD'),
        REGION_NAME='NL',
    )


    connection = objectstore.get_connection(OBJECTSTORE)

    use this connection in below methods
"""

import argparse
import datetime
import logging
import os
import sys

from dateutil import parser as dateparser

# import connection
import objectstore

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

DUMPFOLDER = '/tmp/backups/'
ENV = os.getenv('ENVIRONMENT', 'ACCEPTANCE')


def upload_database(connection, container: str, location: str):

    if location:
        dump = open(location, 'rb')
    else:
        dump = open(f'{DUMPFOLDER}/database.dump', 'rb')

    date = f"{datetime.datetime.now():%Y%m%d-%H%M%S}"

    objectstore.put_object(
        connection,
        f'{container}',
        f'database.{ENV}.{date}.dump',
        # contents=dump.read(),
        contents=dump,
        content_type='application/octet-stream')


def return_file_objects(connection, container, prefix='database'):
    """Given connecton and container find database dumps
    """

    options = []

    meta_data = objectstore.get_full_container_list(
        connection, container, prefix='database')

    for o_info in meta_data:
        expected_file = f'database.{ENV}'
        if o_info['name'].startswith(expected_file):
            dt = dateparser.parse(o_info['last_modified'])
            now = datetime.datetime.now()

            delta = now - dt

            LOG.debug('AGE: %d %s', delta.days, expected_file)

            options.append((dt, o_info))

        options.sort()

    return options


def remove_old_dumps(connection, container: str, days=None):
    """Remove dumps older than x days
    """

    if not days:
        return

    if days < 20:
        LOG.error('A minimum of 20 backups is stored')
        return

    options = return_file_objects(connection, container)

    for dt, o_info in options:
        now = datetime.datetime.now()
        delta = now - dt
        if delta.days > days:
            LOG.info('Deleting %s', o_info['name'])
            objectstore.delete_object(connection, container, o_info)


def download_database(connection, container: str, target: str = ""):
    """
    Download database dump
    """

    meta_data = objectstore.get_full_container_list(
        connection, container, prefix='database')

    options = return_file_objects(connection, container)

    for o_info in meta_data:
        expected_file = f'database.{ENV}'

        LOG.info(o_info['name'])

        if o_info['name'].startswith(expected_file):
            dt = dateparser.parse(o_info['last_modified'])
            # now = datetime.datetime.now()
            options.append((dt, o_info))

        options.sort()

    if not options:
        LOG.error('Dumps missing? ENVIRONMENT wrong? (acceptance / production')
        LOG.error('Environtment {ENV}')
        sys.exit(1)

    newest = options[-1][1]

    LOG.debug('Downloading: %s', (newest['name']))

    target_file = os.path.join(target, expected_file)

    LOG.info('TARGET: %s', target_file)

    if os.path.exists(target_file):
        LOG.info('Already downloaded')
        return

    LOG.error('TARGET does not exists downloading...')

    new_data = objectstore.get_object(connection, newest, container)

    # save output to file!
    with open(target_file, 'wb') as outputzip:
        outputzip.write(new_data)


def run(connection):
    """
    Parse arguments and start upload/download
    """

    parser = argparse.ArgumentParser(description="""
    Process database dumps.

    Either download of upload a dump file to the objectstore.

    downloads the latest dump and uploads with envronment and date
    into given container destination
    """)

    parser.add_argument(
        'location',
        nargs=1,
        default=f'{DUMPFOLDER}/database.{ENV}.dump',
        help="Dump file location")

    parser.add_argument(
        'objectstore',
        nargs=1,
        default=f'{DUMPFOLDER}/database.{ENV}.dump',
        help="Dump file objectstore location")

    parser.add_argument(
        '--download-db',
        action='store_true',
        dest='download',
        default=False,
        help='Download db')

    parser.add_argument(
        '--upload-db',
        action='store_true',
        dest='upload',
        default=False,
        help='Upload db')

    parser.add_argument(
        '--container',
        action='store_true',
        dest='container',
        default=False,
        help='Upload db')

    parser.add_argument(
        '--days',
        type=int,
        nargs=1,
        dest='days',
        default=0,
        help='Days to keep database dumps')

    args = parser.parse_args()

    if args.days:
        LOG.debug('Cleanup old dumps')
        remove_old_dumps(
            connection, args.objectstore[0], args.days[0])
    elif args.download:
        download_database(
            connection, args.objectstore[0], args.location[0])
    elif args.upload:
        upload_database(
            connection, args.objectstore[0], args.location[0])
    else:
        parser.print_help()


def main():
    connection = objectstore.get_connection()
    run(connection)


if __name__ == '__main__':
    main()
