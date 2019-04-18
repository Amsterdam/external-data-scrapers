create table if not exists sum_time (
	id serial,
	setid integer,
	start_time integer,
	end_time integer,
	description varchar(255),
	PRIMARY KEY(id)
);

-- 'upserts'
insert into sum_time(id, setid, start_time, end_time, description) values(1, 1, 6, 9, 'ochtend spits') ON CONFLICT DO NOTHING;
insert into sum_time(id, setid, start_time, end_time, description) values(2, 1, 16, 18, 'avond spits') ON CONFLICT DO NOTHING;
insert into sum_time(id, setid, start_time, end_time, description) values(3, 1, null, null, 'anders') ON CONFLICT DO NOTHING;

create table if not exists sum_ovkv6_speed (
	id bigserial, -- for mapserver 
	bucket integer references sum_time(id),
    vehicle_date date not null,
	dataownercode varchar(255) not null,
	lineplanningnumber varchar(255) not null,
	journeynumber integer not null,
	geo_location geometry(LineString, 4326),
	userstopcode varchar(255),
	prev_userstopcode varchar(255),
	sum_distance integer,
	sum_time integer,
	avg_speed float	
);

-- Enforce unique constraint on combination of a row. 
-- We can abuse this to redo insertions of a partition multiple times and continue on constraint conflicts.
-- (== it is safe to do multiple summaries on the same partition)
CREATE unique INDEX IF NOT exists sum_kv6_day_idx  ON sum_ovkv6_speed (vehicle_date, bucket, dataownercode, lineplanningnumber, journeynumber, geo_location);

insert into sum_ovkv6_speed
	(vehicle_date, bucket, dataownercode, lineplanningnumber, journeynumber, geo_location, userstopcode, prev_userstopcode, sum_distance, sum_time, avg_speed)
select
	o.vehicle::date as grouped_day,
	coalesce((
		select id from sum_time t 
		where (
			(t.start_time >= extract(hour from o.vehicle)::int and t.end_time <= extract(hour from o.vehicle)::int) 
			or (t.start_time is null and t.end_time is null)
		)			
		and setid = 1 -- can store different sets for different slices
		order by t.start_time nulls last limit 1
	), -1) as bucket, -- -1 wil cause fk error
	o.dataownercode,
	o.lineplanningnumber,
	o.journeynumber,
	ST_MakeLine(ST_Transform(o.geo_location, 4326),
				ST_Transform(o.prev_geo_location, 4326)),
	o.userstopcode,
	o.prev_userstopcode,
	sum(o.distance) as sum_distance,
	sum(o.time) as sum_time,
	sum(o.distance) / sum(o.time) * 60*60/1000.0 as avg_speed -- km/hour
from ov_ovkv6 o
where 
	o.geo_location is not null
	and o.prev_geo_location is not null
	and o.distance is not null
	and o.time is not null
	-- get start and end date of current week, will match with ov_kv6raw week partitions
	and o.vehicle >= date_trunc('week', now()::date)
	and o.vehicle < date_trunc('week', now()::date) + interval '1 week'
group by 
	grouped_day,
	o.dataownercode,
	o.lineplanningnumber,
	o.journeynumber,
	o.geo_location,
	o.prev_geo_location,
	o.userstopcode,
	o.prev_userstopcode,	
	bucket
	ON CONFLICT DO NOTHING;


