PARKINGLOCATION_RAW_TO_MODEL_FIELDS = {
    'Id': 'api_id',
    'Name': 'name',
    'PubDate': 'pub_date',
    'Type': 'type',
    'State': 'state',
    'FreeSpaceShort': 'free_space_short',
    'FreeSpaceLong': 'free_space_long',
    'ShortCapacity': 'short_capacity',
    'LongCapacity': 'long_capacity',
    'geometry': 'geometrie'
}

GUIDANCESIGN_RAW_TO_MODEL_FIELDS = {
    'Id': 'api_id',
    'geometry': 'geometrie',
    'Name': 'name',
    'Type': 'type',
    'State': 'state',
    'PubDate': 'pub_date',
    'Removed': 'removed'
}

GUIDANCESIGN_UPDATE_FIELDS = list(GUIDANCESIGN_RAW_TO_MODEL_FIELDS.values()) + ['stadsdeel', 'buurt_code', 'scraped_at']

PARKINGGUIDANCEDISPLAY_RAW_TO_MODEL_FIELDS = {
    'Id': 'api_id',
    'Description': 'description',
    'Type': 'type',
    'Output': 'output',
    'OutputDescription': 'output_description',
}
