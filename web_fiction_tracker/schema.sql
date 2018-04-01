drop table if exists fiction_ffnet;
create table fiction_ffnet(
	id text primary key,
	title text,
	first_chapter_link text,
	chapter int,
	next_chapter_numb int,
	next_chapter_link text,
	last_chapter_numb text,
	hidden boolean,
	folder text
);