# flake8: noqa

INSERT_TRAVELTIME = """
INSERT INTO importer_traveltime (
measurement_site_reference,
computational_method,
number_of_incomplete_input,
number_of_input_values_used,
standard_deviation,
supplier_calculated_data_quality,
duration,
data_error,
measurement_time,
geometrie,
length,
road_type,
stadsdeel,
buurt_code,
scraped_at
)
VALUES {}
"""

INSERT_TRAFFICSPEED = """
INSERT INTO importer_trafficspeed (
measurement_site_reference,
measurement_time,
type,
index,
data_error,
scraped_at,
flow,
speed,
number_of_input_values_used,
standard_deviation,
geometrie,
stadsdeel,
buurt_code
)
VALUES {}
"""

SELECT_STADSDEEL_28992 = "select code, ST_Transform(wkb_geometry, 28992) FROM stadsdeel"
SELECT_BUURT_CODE_28992 = "select code, ST_Transform(wkb_geometry, 28992) FROM buurt_simple"
SELECT_STADSDEEL_4326 = "select code, ST_Transform(wkb_geometry, 4326) FROM stadsdeel"
SELECT_BUURT_CODE_4326 = "select code, ST_Transform(wkb_geometry, 4326) FROM buurt_simple"

INSERT_DAILY_TRAVELTIME_SUMMARY = """
insert into daily_traveltime_summary (
    duration,
    measurement_site_reference,
    geometrie,
    stadsdeel,
    buurt_code,
    length,
    scraped_at
)
select
    avg(duration),
    measurement_site_reference,
    geometrie,
    stadsdeel,
    buurt_code,
    avg(length),
    cast(concat(date(scraped_at), ' ', make_time(cast(Floor(date_part('hour', scraped_at)/6)*6 as integer), 0, 0)) as timestamp)
from importer_traveltime
where
    duration >= 0 {}
group by
    measurement_site_reference,
    geometrie,
    stadsdeel,
    buurt_code,
    cast(concat(date(scraped_at), ' ', make_time(cast(Floor(date_part('hour', scraped_at)/6)*6 as integer), 0, 0)) as timestamp);
"""

INSERT_DAILY_TRAFFICSPEED_SUMMARY = """
insert into daily_trafficspeed_summary (
    speed,
    measurement_site_reference,
    geometrie,
    stadsdeel,
    buurt_code,
    length,
    scraped_at
)
select
    avg(speed),
    measurement_site_reference,
    geometrie,
    stadsdeel,
    buurt_code,
    avg(length),
    cast(concat(date(scraped_at), ' ', make_time(cast(Floor(date_part('hour', scraped_at)/6)*6 as integer), 0, 0)) as timestamp)
from importer_trafficspeed
where
    speed >= 0 {}
group by
    measurement_site_reference,
    geometrie,
    stadsdeel,
    buurt_code,
    cast(concat(date(scraped_at), ' ', make_time(cast(Floor(date_part('hour', scraped_at)/6)*6 as integer), 0, 0)) as timestamp);
"""
SCRAPED_AT_WHERE_CLAUSE = "and date(scraped_at)='{}'"
