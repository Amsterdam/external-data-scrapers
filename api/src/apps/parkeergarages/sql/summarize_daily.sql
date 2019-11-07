create table if not exists parkeergarages.parkinglocation_summary (
	id bigserial, -- for mapserver 
	api_id varchar(255) not null,
	name varchar(255) not null,
	pub_date timestamptz not null,
    date date not null,
    iso_year integer not null,
    week integer not null, 
    hour integer not null, 
	iso_day integer not null,
	state varchar(10),
	free_space_short integer,
	free_space_long integer,
	short_capacity integer,
	long_capacity integer,
	short_space_ratio float8,
	long_space_ratio float8,
	stadsdeel varchar(1),
	buurt_code varchar(10),
	nber integer 
);

-- Enforce unique constraint on combination of a row. 
-- We can abuse this to redo insertions of a day multiple times and continue on constraint conflicts.
-- (== it is safe to do multiple summaries on the same day)
CREATE unique INDEX IF NOT exists parkinglocation_summary_day_id 
ON parkeergarages.parkinglocation_summary (pub_date, api_id, hour, nber); 

with tmp as (
    select
        api_id,
        name, 
        pub_date,
        cast(pub_date as date) as date,
        extract(isoyear from pub_date) as iso_year, 
        extract(week from pub_date) as week,
        extract(hour from pub_date) as hour,
        extract(isodow from pub_date) as iso_day, 
        state, 
        free_space_short, 
        free_space_long, 
        short_capacity, 
        long_capacity, 
        free_space_short*1.0/nullif(short_capacity, 0) as short_space_ratio,
        free_space_long*1.0/nullif(long_capacity, 0) as long_space_ratio,
        stadsdeel, 
        buurt_code,
        row_number() over (partition by "name", (cast(pub_date as date), (extract(hour from pub_date)) ) order by pub_date desc) 
        as nber -- Take only last entry in the hour
    from 
        public.importer_parkinglocation
    where
        scraped_at::date = now()::date -1
    order by pub_date desc
    )
insert into parkeergarages.parkinglocation_summary (
	api_id, 
	name, 
	pub_date, 
	date, 
	iso_year, 
	week, 
	hour, 
	iso_day, 
	state, 
	free_space_short, 
	free_space_long, 
	short_capacity, 
	long_capacity, 
	short_space_ratio, 
	long_space_ratio, 
	stadsdeel, 
	buurt_code, 
	nber
	)
select *
from tmp where nber=1 
on conflict do nothing;
