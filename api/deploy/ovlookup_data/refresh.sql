\set ON_ERROR_STOP on

-- bounding box around amsterdam
-- [52.455636, 4.714153, 52.256733, 5.070706]
\set TOPLEFT_LAT 52.455636::REAL
\set TOPLEFT_LON 4.714153::REAL
\set BOTTOMRIGHT_LAT 52.256733::REAL
\set BOTTOMRIGHT_LON 5.070706::REAL

-- Reload stops
DROP TABLE IF EXISTS csv_stops;
CREATE TABLE csv_stops (
    stop_id                 VARCHAR(255) NOT NULL,
    stop_code               VARCHAR(255),
    stop_name               VARCHAR(255),
    stop_lat                REAL NOT NULL,
    stop_lon                REAL NOT NULL,
    location_type           VARCHAR(255),
    parent_station          VARCHAR(255),
    stop_timezone           VARCHAR(255),
    wheelchair_boarding     SMALLINT,
    platform_code           VARCHAR(255),
    zone_id                 VARCHAR(255),
    CONSTRAINT csv_stops_pkey PRIMARY KEY(stop_id)
);

\COPY csv_stops FROM '/app/stops.txt' delimiter ',' csv header;
ANALYZE VERBOSE csv_stops;

-- reload route shapes
DROP TABLE IF EXISTS csv_shapes;
CREATE TABLE csv_shapes (
    shape_id                INTEGER NOT NULL,
    shape_pt_sequence       SMALLINT NOT NULL,
    shape_pt_lat            REAL NOT NULL,
    shape_pt_lon            REAL NOT NULL,
    shape_dist_traveled     INTEGER NOT NULL,
    CONSTRAINT csv_shapes_pkey PRIMARY KEY(shape_id, shape_pt_sequence)
);

\COPY csv_shapes FROM '/app/shapes.txt' delimiter ',' csv header;

-- CREATE index csv_shapes_ams_bbox_partial_idx ON csv_shapes(shape_pt_lat, shape_pt_lon)
--    WHERE :TOPLEFT_LAT >= shape_pt_lat AND :BOTTOMRIGHT_LAT <= shape_pt_lat
--    AND :TOPLEFT_LON <= shape_pt_lon AND :BOTTOMRIGHT_LON >= shape_pt_lon;
ANALYZE VERBOSE csv_shapes;

-- reload trips
DROP TABLE IF EXISTS csv_trips;
CREATE TABLE csv_trips (
    route_id                INTEGER NOT NULL,
    service_id              SMALLINT NOT NULL,
    trip_id                 INTEGER NOT NULL,
    realtime_trip_id        VARCHAR(255) NOT NULL,
    trip_headsign           VARCHAR(255),
    trip_short_name         VARCHAR(255),
    trip_long_name          VARCHAR(255),
    direction_id            SMALLINT NOT NULL,
    block_id                INTEGER,
    shape_id                INTEGER,
    wheelchair_accessible   SMALLINT,
    bikes_allowed           SMALLINT,
    CONSTRAINT csv_trips_pkey PRIMARY KEY(route_id, trip_id, service_id)
);

\COPY csv_trips FROM '/app/trips.txt' DELIMITER ',' CSV HEADER;
CREATE INDEX csv_trips_rtid_idx on csv_trips(realtime_trip_id);
CREATE INDEX csv_trips_shape_id_idx on csv_trips(shape_id);

ANALYZE VERBOSE csv_trips;

BEGIN;
-- refresh ovstop
DELETE FROM ov_ovstop;
INSERT INTO ov_ovstop
SELECT DISTINCT ON (stop_code)
    stop_code,
    stop_name,
    ST_SetSRID(ST_MakePoint(CAST(stop_lon AS FLOAT), CAST(stop_lat AS FLOAT)), 4326)
FROM
    csv_stops
WHERE
    stop_code is not null;

-- refresh ovroutes
DELETE FROM ov_ovroutes;
INSERT INTO ov_ovroutes
SELECT DISTINCT ON (t.realtime_trip_id)
    t.realtime_trip_id,
    t.route_id,
    t.service_id,
    t.trip_id,
    t.trip_headsign,
    t.trip_short_name,
    t.trip_long_name
FROM 
    csv_trips t, csv_shapes s
WHERE 
    t.shape_id = s.shape_id AND t.realtime_trip_id IS NOT NULL
    AND :TOPLEFT_LAT >= shape_pt_lat AND :BOTTOMRIGHT_LAT <= shape_pt_lat
    AND :TOPLEFT_LON <= shape_pt_lon AND :BOTTOMRIGHT_LON >= shape_pt_lon;

COMMIT;