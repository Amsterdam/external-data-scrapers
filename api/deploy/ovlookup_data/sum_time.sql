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
