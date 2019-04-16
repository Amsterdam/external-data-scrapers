DROP TABLE IF EXISTS sum_ovkv6_speed;
DROP TABLE IF EXISTS sum_time;

create table sum_time (
	id serial,
	start_time integer,
	end_time integer,
	description varchar(255),
	PRIMARY KEY(id)
);

insert into sum_time(start_time, end_time, description) values(6, 9, 'ochtend spits');
insert into sum_time(start_time, end_time, description) values(16, 18, 'avond spits');
insert into sum_time(start_time, end_time, description) values(null, null, 'anders');



create table sum_ovkv6_speed (
	tid integer references sum_time(id),
    day date not null,
	dataownercode varchar(255) not null,
	lineplanningnumber varchar(255) not null,
	journeynumber integer not null,
	sum_distance integer,
	sum_time integer,
	avg_speed float	
);



select
	coalesce((
		select id from sum_time t 
		where t.start_time >= extract(hour from o.vehicle)::int
		and t.end_time <= extract(hour from o.vehicle)::int
	), 3) as bucket,
	o.vehicle::date as grouped_day,
	o.dataownercode,
	o.lineplanningnumber,
	o.journeynumber,
	o.geo_location,
	o.prev_geo_location,
	o.userstopcode,
	o.prev_userstopcode,
	sum(o.distance) as sum_distance,
	sum(o.time) as sum_time,
	sum(o.distance) / sum(o.time) * 60*60/1000.0 as avg_speed
from ov_ovkv6 o
where 
	o.geo_location is not null
	and o.prev_geo_location is not null
	and o.distance is not null
	and o.time is not null
group by 
	grouped_day,
	o.dataownercode,
	o.lineplanningnumber,
	o.journeynumber,
	o.geo_location,
	o.prev_geo_location,
	o.userstopcode,
	o.prev_userstopcode,	
	bucket;


