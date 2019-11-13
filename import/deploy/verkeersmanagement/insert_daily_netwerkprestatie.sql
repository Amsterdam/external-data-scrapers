insert into verkeersmanagement.netwerkprestatie_detail 
select 	qq.measurement_site_reference, 
			qq.hour_nr, 
			qq.week_nr, 
			qq.dow_nr, 
			qq.datum,
			qq.target_speed,
			case when sum(qq.duration - qq.target_time) / sum(target_time) + 1 > 1
				then round(greatest(5.5 - log(4^(1.0/4.5), (sum(qq.duration - qq.target_time) / sum(target_time) + 1)::numeric), 1), 2)
				else round(least(5.5 + log(4^(1.0/4.5), 1/(sum(qq.duration - qq.target_time) / sum(target_time) + 1)::numeric), 10), 2) end as cijfer
			--into netwerkprestatie_detail
	from (
		select 	q.measurement_site_reference, 
				q.measurement_time, 
				extract('week' from q.measurement_time)::int as week_nr,
				extract('isodow' from q.measurement_time)::int as dow_nr,
				extract('hour' from q.measurement_time)::int as hour_nr,
				q.measurement_time::date as datum,
				case when extract('hour' from q.measurement_time)::int in (7,8,16,17,18) then true else false end as spits_bool,
				q.duration,
				q.geometrie as geom, 
				q.stadsdeel, 
				q.length,
				q.speedlimit as max_speed, 
				q.streefwaarde as target_speed, 
				round(q.length / (q.streefwaarde / 3.6), 2) as target_time
		from (
			select 	s.measurement_site_reference,
					s.measurement_time::timestamp at time zone 'utc' at time zone 'cet' as measurement_time, 
					COALESCE(s.duration, NULL) as duration, 
					s.geometrie,
					s.stadsdeel,
					COALESCE(s.length, NULL) as length,
					h.speedlimit, 
					h.streefwaarde
			from public.importer_traveltime as s
			join verkeersmanagement.hulptabel as h
			on s.measurement_site_reference = h.measurement_site_reference
			where s.data_error::bool = false
			and scraped_at::date = now()::date -1 
		) as q
	) as qq
	group by qq.measurement_site_reference, qq.hour_nr, qq.week_nr, qq.dow_nr, qq.datum, qq.target_speed 

