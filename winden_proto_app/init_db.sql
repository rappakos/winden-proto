

CREATE TABLE IF NOT EXISTS piloten (
	pilot_id TEXT NOT NULL UNIQUE PRIMARY KEY,
	[name] TEXT NOT NULL,
	[status_txt] TEXT NOT NULL, -- could be FK to status 
    [gewicht] int null,
	verein TEXT NULL
);

INSERT OR IGNORE INTO piloten (pilot_id,[name] ,[status_txt])
VALUES
('Akos','Akos','W')
,('Orsi','Orsi','W')
,('Helmut','Helmut','W')
,('Michi','Michi','W')
,('Beate','Beate','M')
,('Martin','Martin','M')
,('Tommi','Tommi','NG')
,('Markus','Markus','G')