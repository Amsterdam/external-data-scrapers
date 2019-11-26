CREATE TABLE IF NOT EXISTS verkeersmanagement.hulptabel (
	measurement_site_reference varchar(80) NULL,
	id int8 NULL,
	speedlimit numeric NULL,
	streefwaarde int4 NULL,
	length float8 NULL,
	geom geometry(MULTILINESTRING, 28992) NULL
);


CREATE TABLE IF NOT EXISTS verkeersmanagement.netwerkprestatie_detail (
	measurement_site_reference varchar(255),
    hour int4 NULL,
    week int4 NULL,
    dow int4 NULL,
    iso_year integer not null,
    datum timestamp NULL,
    target_speed int4 NULL,
    cijfer float8 NULL
);

CREATE OR REPLACE VIEW verkeersmanagement.netwerkprestatie_detail_percentile_ref AS
    select  
        measurement_site_reference, 
		hour, 
	    dow, 
	    percentile_cont(0.1) WITHIN GROUP (ORDER BY cijfer) as p10,
	    percentile_cont(0.2) WITHIN GROUP (ORDER BY cijfer) as p20,
	    percentile_cont(0.5) WITHIN GROUP (ORDER BY cijfer) as p50,
	    percentile_cont(0.8) WITHIN GROUP (ORDER BY cijfer) as p80,
	    percentile_cont(0.9) WITHIN GROUP (ORDER BY cijfer) as p90
	from
        verkeersmanagement.netwerkprestatie_detail
	group by 
        measurement_site_reference, 
		hour,
	    dow;
	    
CREATE OR REPLACE VIEW verkeersmanagement.visualization_view as
	select 
		a.*, 
		b.p10, 
		b.p20, 
		b.p50, 
		b.p80, 
		b.p90
from 
	verkeersmanagement.netwerkprestatie_detail as a
left join 
	verkeersmanagement.netwerkprestatie_detail_percentile_ref as b
on 
	a.measurement_site_reference = b.measurement_site_reference 
	and a.hour = b.hour 
	and a.dow = b.dow;
