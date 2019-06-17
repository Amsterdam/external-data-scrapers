-- Should be already set on the server but to be sure when testing locally.
set time zone 'Europe/Amsterdam';

create table if not exists sum_ovkv6_tramlines_speed (
	id bigserial, -- for mapserver 
	bucket integer references sum_time(id),
    vehicle_date date not null,
	dataownercode varchar(255) not null,
	lineplanningnumber varchar(255) not null,
	userstopcode varchar(255),
	prev_userstopcode varchar(255),
	sum_distance integer,
	sum_time integer,
	avg_speed float,
	geo_location geometry(MultiLineString, 4326),
    direction integer,
    trajectory_id integer references trajectories_tramlines_govi(id),
    stop_sequence integer,
    vehiclenumber integer
);
-- Enforce unique constraint on combination of a row. 
-- We can abuse this to redo insertions of a partition multiple times and continue on constraint conflicts.
-- (== it is safe to do multiple summaries on the same partition)
CREATE unique INDEX IF NOT exists sum_kv6_tl_day_idx  ON sum_ovkv6_tramlines_speed (vehicle_date, bucket, lineplanningnumber, vehiclenumber, userstopcode, stop_sequence);

insert into sum_ovkv6_tramlines_speed (
    vehicle_date, 
    bucket, 
    dataownercode, 
    lineplanningnumber, 
    userstopcode, 
    prev_userstopcode, 
    sum_distance, 
    sum_time, 
    avg_speed, 
    geo_location, 
    direction, 
    trajectory_id, 
    stop_sequence,
    vehiclenumber)
select
	o.vehicle::date as grouped_day,
	coalesce((
		select id from sum_time t 
		where (
			(
                t.start_time <= extract(hour from o.vehicle)::int and 
                t.end_time >= extract(hour from o.vehicle)::int) 
			or (t.start_time is null and t.end_time is null)
		)			
		and setid = 1 -- can store different sets for different slices
		order by t.start_time nulls last limit 1
	), -1) as bucket, -- -1 wil cause fk error
	o.dataownercode,
	o.lineplanningnumber,
	o.userstopcode,
	o.prev_userstopcode,
	sum(o.distance) as sum_distance,
	sum(o.time) as sum_time,
	coalesce(sum(o.distance) /NULLIF(sum(o.time), 0), 0) * 60*60/1000.0 as avg_speed, -- km/hour
    ST_Transform(traj.wkb_geometry, 4326),
    traj.richting,
    traj.id,
	rs.stop_sequence,
	o.vehiclenumber
from ov_ovkv6 o, trajectories_tramlines_govi traj, ov_ovroutesection as rs
where 
	o.distance is not null
	and o.time is not null
    and dataownercode = 'GVB'
    and o.userstopcode != 'Not found' and o.userstopcode != ''
    and traj.source_stopid::int = o.prev_userstopcode::int 
    and traj.target_stopid::int = o.userstopcode::int
    and traj.lineplanningnumber::int = o.lineplanningnumber::int
    and rs.route_id = CONCAT(o.dataownercode, ':', o.lineplanningnumber, ':', o.journeynumber)
    and rs.stop_code::int = o.userstopcode::int
	-- get start and end date of current week, will match with ov_kv6raw week partitions
	and o.vehicle >= date_trunc('week', now()::date)
	and o.vehicle < date_trunc('week', now()::date) + interval '1 week'
group by 
	grouped_day,
	o.dataownercode,
	o.lineplanningnumber,
	o.geo_location,
	o.userstopcode,
	o.prev_userstopcode,
	o.vehiclenumber,
    traj.id,
	bucket,
    rs.stop_sequence
ON CONFLICT DO NOTHING;
