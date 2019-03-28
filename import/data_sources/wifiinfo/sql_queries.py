INSERT_WIFIINFO = """
INSERT INTO importer_wifiinfo (
unique_id,
sensor,
first_detection,
last_detection,
strongest_signal_timestamp,
strongest_signal_rssi,
csv_name
)
SELECT
    unique_id,
    sensor,
    first_detection,
    last_detection,
    strongest_signal_timestamp,
    strongest_signal_rssi,
    '{csv_name}'
FROM
    temp_importer_wifiinfo
"""
