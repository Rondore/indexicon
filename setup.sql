create table source (
	s_id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
	s_url TEXT,
	s_last_crawl INTEGER NOT NULL DEFAULT 0,
	s_enabled BIT NOT NULL DEFAULT 1
);

create table file (
	f_id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
	f_source INTEGER,
	f_url TEXT,
	f_name TEXT,
	f_search_text TEXT
);

create table error (
	e_id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
	e_source INTEGER,
	e_time INTEGER NOT NULL
);

create table passover (
	p_id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
	p_source INTEGER,
	p_directory TEXT
);