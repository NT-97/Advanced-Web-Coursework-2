DROP TABLE if EXISTS users;
DROP TABLE if EXISTS classes;

CREATE TABLE  users  (
	 user 	TEXT,
	 password 	TEXT,
	 pay 	REAL,
	PRIMARY KEY( user )
);

CREATE TABLE  classes  (
	 day 	INTEGER,
	 month 	INTEGER,
	 year 	INTEGER,
	 class_start 	TEXT,
	 class_end 	TEXT,
	 moduleID 	TEXT NOT NULL,
	 moduleName 	TEXT NOT NULL,
	 lecturer 	TEXT,
	 user 	TEXT,
	PRIMARY KEY( day , month , year )
);

INSERT INTO users(user, password, pay)
VALUES ('michael', 'test', '10.0');

INSERT INTO classes(day,month,year,class_start,class_end,moduleID,moduleName,lecturer,user)
VALUES(28,12,2018,12.00,13.00,SET09103,Soft Eng, Simon Wells, michael)

