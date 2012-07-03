drop table if exists tasks;
create table tasks (
	id integer primary key autoincrement,
	task string not null,
	startdate string not null,
	enddate string not null,
	priority integer not null
);
