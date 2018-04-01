drop table if exists entries;
create table entries(
	id text primary key,
	title text,
	chapter int,
	next_chapter_numb int,
	next_chapter_link text,
	last_chapter_available text
);