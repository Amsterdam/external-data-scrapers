-- Should be already set on the server but to be sure when testing locally.
set time zone 'Europe/Amsterdam';

create table if not exists ovfiets.ovfiets_summary (
	id bigserial, -- for mapserver 
	name varchar(255) not null,
	location_code varchar(255) not null,
    fetch_time timestamptz not null,
    date date not null,
    iso_year integer not null,
    week integer not null, 
    hour integer not null, 
	iso_day integer not null,
	rental_bikes integer,
	availability_ratio float8,
	availability_percentage integer,
	maximum_availability integer,
	nber integer 
);

-- Enforce unique constraint on combination of a row. 
-- We can abuse this to redo insertions of a day multiple times and continue on constraint conflicts.
-- (== it is safe to do multiple summaries on the same day)
CREATE unique INDEX IF NOT exists ovfiets_summary_day_id 
ON ovfiets.ovfiets_summary (fetch_time, location_code, hour, nber); 

with tmp as(
	select
        name, 
        location_code,
        fetch_time,
        extract(hour from fetch_time) as hour,
        extract(week from fetch_time) as week,
        cast(fetch_time as date) as date,
        extract(isodow from fetch_time) as iso_day, 
        extract(isoyear from fetch_time) as iso_year, 
        rental_bikes,
        rental_bikes*1.0/max(rental_bikes) over (partition by "location_code")  as availability_ratio,
        rental_bikes*100/max(rental_bikes) over (partition by "location_code") as availability_percentage,
        max(rental_bikes) over (partition by "location_code") as maximum_availability,
        row_number() over (
            partition by "location_code", (cast(fetch_time as date), extract(hour from fetch_time)) order by fetch_time desc
        ) as nber -- Take only last entry in the hour
    from public.importer_ovfiets
    where 
        scraped_at::date = now()::date -1 
        and location_code in (
                'asa001',
                'asb003',
                'asb001',
                'asd008',
                'asd002',
                'ads007',
                'asd009',
                'asd006',
                'asd001',
                'asdm001',
                'adsz001',
                'asdz003',
                'ass001',
                'ass002',
                'rai001',
                'rai002',
                'ASDZ004'
            )
    order by location_code, fetch_time desc
)
insert into ovfiets.ovfiets_summary (
    name, 
    location_code, 
    fetch_time, 
    hour, 
    week, 
    date, 
    iso_day, 
    iso_year, 
    rental_bikes, 
    availability_ratio, 
    availability_percentage, 
    maximum_availability,
    nber
)
select * from tmp where nber=1
on conflict do nothing;
