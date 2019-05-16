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

insert into daily_traveltime_summary
    (grouped_day, bucket, duration, measurement_site_reference, geometrie, stadsdeel, buurt_code, velocity)
select 
    i.measurement_time::date as grouped_day,
    coalesce((
        select id from sum_time t
        where (
            (t.start_time >= extract(hour from i.measurement_time)::int and t.end_time <= extract(hour from i.measurement_time)::int)
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
    -- Avoid division by zero
    avg(coalesce(length/NULLIF(duration, 0), 0)*3.6) as velocity
from importer_traveltime i
where
    i.data_error=false
    and i.duration >= 0
    and i.measurement_time::date != now()::date
    and i.measurement_time::date not in (select grouped_day from daily_traveltime_summary)
group by 
	grouped_day,
    i.measurement_site_reference,
    i.geometrie,
    i.stadsdeel,
    i.buurt_code,
	bucket
	ON CONFLICT DO NOTHING;
