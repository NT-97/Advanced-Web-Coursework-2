DROP TABLE if EXISTS users;
DROP TABLE if EXISTS events;

CREATE TABLE users (
	user	TEXT,
	password	TEXT,
	pay	REAL,
	PRIMARY KEY(user)
);

CREATE TABLE events (
	day	INTEGER,
	month	INTEGER,
	year
  	INTEGER,
	start_time	TEXT,
	end_time	TEXT,
	details	TEXT,
	user	TEXT,
	PRIMARY KEY(day,month,year)
);

INSERT INTO users(user, password, pay)
VALUES ('michael', 'test', '10.0');

