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
SELECT_BUURT_CODE_28992 = "select code, ST_Transform(wkb_geometry, 28992) FROM buurt"
SELECT_STADSDEEL_4326 = "select code, ST_Transform(wkb_geometry, 4326) FROM stadsdeel"
SELECT_BUURT_CODE_4326 = "select code, ST_Transform(wkb_geometry, 4326) FROM buurt"
