"""
We use the objectstore to get/upload the latest and greatest.

import objectstore

give example config:

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

    loop over all items in 'container/dirname'

    meta_data = connection.get_full_container_list(connection, 'dirname')

    now you can loop over meta data of files

    for file_info in meta_data:
        if file_info['name'].endswith(expected_file):

        LOG.debug('Downloading: %s', (expected_file))

        new_data = objectstore.get_object(
            connection, o_info, container)

"""

import logging
import os

from swiftclient.client import Connection

# import pprint


LOG = logging.getLogger('objectstore')


logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("swiftclient").setLevel(logging.WARNING)


def make_config_from_env():
    OBJECTSTORE = dict(
        VERSION='2.0',
        AUTHURL='https://identity.stack.cloudvps.com/v2.0',
        TENANT_NAME=os.getenv('TENANT_NAME'),
        TENANT_ID=os.getenv('TENANT_ID'),
        USER=os.getenv('OBJECTSTORE_USER'),
        PASSWORD=os.getenv('OBJECTSTORE_PASSWORD'),
        REGION_NAME='NL',
    )

    # pp = pprint.PrettyPrinter(6)
    # LOG.debug(pp.pprint(OBJECTSTORE))

    return OBJECTSTORE


def get_connection(store_settings: dict = {}) -> Connection:
    """
    get an objectsctore connection
    """
    store = store_settings

    if not store_settings:
        store = make_config_from_env()

    os_options = {
        'tenant_id': store['TENANT_ID'],
        'region_name': store['REGION_NAME'],
        # 'endpoint_type': 'internalURL'
    }

    # when we are running in cloudvps we should use internal urls
    use_internal = os.getenv('OBJECTSTORE_LOCAL', '')
    if use_internal:
        os_options['endpoint_type'] = 'internalURL'

    connection = Connection(
        authurl=store['AUTHURL'],
        user=store['USER'],
        key=store['PASSWORD'],
        tenant_name=store['TENANT_NAME'],
        auth_version=store['VERSION'],
        os_options=os_options
    )

    return connection


def get_full_container_list(conn, container, **kwargs) -> list:
    limit = 10000
    kwargs['limit'] = limit
    page = []

    _, page = conn.get_container(container, **kwargs)
    lastpage = page
    for object_info in lastpage:
        yield object_info

    while len(lastpage) == limit:
        # keep getting pages..
        kwargs['marker'] = lastpage['name']
        _, lastpage = conn.get_container(container, **kwargs)
        for object_info in lastpage:
            yield object_info


def get_object(connection, object_meta_data: dict, dirname: str):
    """
    Download object from objectstore.
    object_meta_data is an object retured when
    using 'get_full_container_list'
    """
    return connection.get_object(dirname, object_meta_data['name'])[1]


def put_object(
        connection, container: str, object_name: str,
        contents, content_type: str) -> None:
    """
    Put file to objectstore

    container == "path/in/store"
    object_name = "your_file_name.txt"
    contents=thefiledata (fileobject) open('ourfile', 'rb')
    content_type='csv'  / 'application/json' .. etc
    """

    connection.put_object(
        container, object_name, contents=contents,
        content_type=content_type)


def delete_object(connection, container: str, object_meta_data: dict) -> None:
    """
    Delete single object from objectstore
    """
    connection.delete_object(container, object_meta_data['name'])
