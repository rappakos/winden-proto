

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
,('Markus','Markus','G');

CREATE TABLE IF NOT EXISTS winden (
	winde_id TEXT NOT NULL UNIQUE PRIMARY KEY,
	[name] TEXT NOT NULL,
	[active] BIT NOT NULL,
    [baujahr] int not null
);

INSERT OR IGNORE INTO winden (winde_id,[name],[active],[baujahr])
VALUES
('ELOWIN','ELOWIN',1,2022)
,('Kella','Kella',0,1975);

CREATE TABLE IF NOT EXISTS schlepps (
			[schlepp_id] integer primary key autoincrement,
	     	[winden_id] text not null,
            [wf_id] text not null,
            [ewf_id] text null,
            [pilot_id]  text not null,
            [datum] text not null, -- ISO YYYY-MM-DD
            [status] text not null default 'started',
            [schlepp_start] datetime default current_timestamp,
            [status_date] datetime default current_timestamp,
			FOREIGN KEY(winden_id) REFERENCES winden(winden_id)
			FOREIGN KEY(wf_id) REFERENCES piloten(pilot_id)
			FOREIGN KEY(pilot_id) REFERENCES piloten(pilot_id)
);