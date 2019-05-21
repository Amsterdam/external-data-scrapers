create table if not exists sum_time (
	id serial,
	setid integer,
	start_time integer,
	end_time integer,
	description varchar(255),
	PRIMARY KEY(id)
);

-- 'upserts'
insert into sum_time(id, setid, start_time, end_time, description) values(1, 1, 6, 9, 'Morning rushhour') ON CONFLICT DO NOTHING;
insert into sum_time(id, setid, start_time, end_time, description) values(2, 1, 16, 18, 'Evening rushhour') ON CONFLICT DO NOTHING;
insert into sum_time(id, setid, start_time, end_time, description) values(3, 1, null, null, 'Rest of day') ON CONFLICT DO NOTHING;

insert into daily_traveltime_summary
    (grouped_day, bucket, duration, measurement_site_reference, geometrie, stadsdeel, buurt_code, road_type, avg_speed)
select 
    i.measurement_time::date as grouped_day,
    coalesce((
        select id from sum_time t
        where (
            (t.start_time <= extract(hour from i.measurement_time)::int and t.end_time >= extract(hour from i.measurement_time)::int)
            or (t.start_time is null and t.end_time is null)
        )
        and setid = 1 -- can store different sets for different slices
        order by t.start_time nulls last limit 1
    ), -1) as bucket, -- -1 will cause fk error
    avg(i.duration),
    i.measurement_site_reference,
    i.geometrie,
    i.stadsdeel,
    i.buurt_code,
    i.road_type,
    -- Avoid division by zero
    avg(coalesce(length/NULLIF(duration, 0), 0)*3.6) as avg_speed
from importer_traveltime i
where
    i.data_error=false
    and i.duration >= -1
    and i.measurement_time::date = now()::date -1
group by 
	grouped_day,
    i.measurement_site_reference,
    i.geometrie,
    i.stadsdeel,
    i.buurt_code,
    i.road_type,
	bucket
ON CONFLICT DO NOTHING;
