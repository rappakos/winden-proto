
/* RESET: add RESET_DB = 1 in .env */

CREATE TABLE IF NOT EXISTS winden (
	[winde_id] TEXT NOT NULL UNIQUE PRIMARY KEY,
	[name] TEXT NOT NULL,
	[active] BIT NOT NULL,
    [baujahr] int not null
);

INSERT OR IGNORE INTO winden (winde_id,[name],[active],[baujahr])
VALUES
('ELOWIN','ELOWIN',1,2022)
,('Kella','Kella',0,1975);

CREATE TABLE IF NOT EXISTS piloten (
	pilot_id TEXT NOT NULL UNIQUE PRIMARY KEY,
	[name] TEXT NOT NULL,
	[status_txt] TEXT NOT NULL, -- could be FK to status G / NG / M / WIA / WF / EWF
    [zugkraft] int null CONSTRAINT CHK_zugkraft CHECK (zugkraft is null or (zugkraft > 0 and zugkraft < 150)),
	[verein] TEXT NULL, -- free text
	[calendar_id] TEXT NULL,
	[create_timestamp] datetime not null default current_timestamp
);

INSERT OR IGNORE INTO piloten ([status_txt],[calendar_id],pilot_id,[name],[verein])
VALUES 
('W','f_26',   'Akos','Akos Rapp', null ), 
('M','f_123',  'Charlotte','Charlotte P.', null ), 
('M','f_120',  'DietmarS','Dietmar Strothmann', null ), 
('WF','f_30',  'Manfred','Manfred K.', null ), 
('WF','f_13',  'Matthias','Matthias Beu.', null ),
('EWF','f_7',  'MichaelH','Michael Hae.', null ), 
('WF','f_25',  'ThomasH','Thomas Heimes', null ), 
('WF','f_90',  'UtzR','Utz', null ), 
('WF','f_147', 'Wolfgang','Wolfgang', null ), 
('NG','f_144', 'AnnaG','Anna Grube', 'GSC W.' ), 
('M','f_34',   'BeateW','Beate W.', null ), 
('WF','f_125', 'ChristianD','Christian Dörges', null ), 
('WF','f_21',  'DanielB','Daniel B.', null ), 
('M','f_141',  'DirkF','Dirk F.', null ), 
('M','f_55',   'HansH','Hans H. aus F.', null ), 
('EWF','f_117','HelmutF','Helmut Fischer', null ), 
('M','f_122',  'JanS','Jan  Strothmann', null ), 
('NG','f_146', 'JanH','Jan H. GSCL', 'GSCL' ), 
('G','f_143',  'JonathanB','Jonathan Balke', null ), 
('NG','f_129', 'JörgH ','Jörg Hiersemann', 'GSCL' ),  -- ?
('G','f_142',  'MartinGeb ','Martin Gebhard', null ), 
('M','f_85',   'MartinF ','Martin Frevert', null ), 
('MG','f_88',  'MichaelK','Michael König', null ), -- ?
('WF','f_27',  'Orsi','Orsi P.', null ), 
('WF','f_17',  'Sabine','Sabine Kl.', null ), 
('G','f_131',  'SebastianR','Sebastian Ritter', null ), 
('WF','f_8',   'SilkeF','Silke F.', null ), 
('M','f_65',   'JohannesM','Tandem Johannes Meyer', null ), 
('NG','f_145', 'ThomasG','Thomas Grube', 'GSC W.'  ), 
('M','f_127',  'Thoralf','Thoralf', null ), 
('WF','f_14',  'TinaS','Tina S.', null ), 
('NG','f_12',  'TommiO','Tommi O.', null );


CREATE TABLE IF NOT EXISTS flying_days (
	[datum] DATE NOT NULL 
			CONSTRAINT CHK_flugtag_datum CHECK (datum==strftime('%Y-%m-%d',datum)),
	[pilot_list] BIT NULL,
	[active_winde_id] TEXT NULL,
	[winde_aufgebaut] datetime null,
	[winde_abgebaut] datetime null,
	[winde_abgestellt] datetime null,
	[active_wf] TEXT NULL,
	[active_ewf] TEXT NULL,
	[closed] datetime null,
	[create_timestamp] datetime not null default current_timestamp,
	FOREIGN KEY([active_wf]) REFERENCES piloten(pilot_id),
	FOREIGN KEY([active_ewf]) REFERENCES piloten(pilot_id),
	FOREIGN KEY([active_winde_id]) REFERENCES winden([winde_id])
);

CREATE TABLE IF NOT EXISTS pilot_list (
		[datum] DATE NOT NULL 
			CONSTRAINT CHK_pilot_list_datum CHECK (datum==strftime('%Y-%m-%d',datum)),
		[pilot_id] TEXT NOT NULL,
		[added_timestamp] datetime not null default current_timestamp,
		FOREIGN KEY(pilot_id) REFERENCES piloten(pilot_id),
		CONSTRAINT PK_protocolquestions UNIQUE([datum],[pilot_id])
);


CREATE TABLE IF NOT EXISTS schlepps (
			[schlepp_id] integer primary key autoincrement,
	     	[winde_id] text not null,
            [wf_id] text not null,
            [ewf_id] text null,
            [pilot_id]  text not null,
            [datum] text not null CONSTRAINT CHK_datum CHECK (datum==strftime('%Y-%m-%d',datum)), -- ISO YYYY-MM-DD
            [status] text not null default 'started', -- started / completed / canceled
            [schlepp_start] datetime default current_timestamp,
            [status_date] datetime default current_timestamp,
			[comment] text null,
			FOREIGN KEY(winde_id) REFERENCES winden(winde_id),
			FOREIGN KEY(wf_id) REFERENCES piloten(pilot_id),
			FOREIGN KEY(ewf_id) REFERENCES piloten(pilot_id),
			FOREIGN KEY(pilot_id) REFERENCES piloten(pilot_id)
);

/* OLD SCHEMA : */

CREATE TABLE IF NOT EXISTS protocolquestions (
	[id] integer primary key autoincrement,
	[question_id] integer not null,
	[type] text not null, -- aufbau / abbau / abstellen
	[question] text not null,
	CONSTRAINT PK_protocolquestions UNIQUE([question_id],[type])

);

--DELETE FROM protocolquestions;

INSERT OR IGNORE INTO protocolquestions ([question_id],[type],[question])
VALUES
(1,'aufbau','Anh&auml;nger zum Startplatz ausgerichtet ?'),
(2,'aufbau','Handbremse angezogen ?'),
(3,'aufbau','Seitlichen St&uuml;tzen ausgefahren ?'),
(4,'aufbau','St&uuml;tzrad ausgefahren ?'),
(5,'aufbau','Falls abgekoppelt: Bremskeile untergelegt ?'),
(6,'aufbau','Plane sicher gelagert ?'),
(7,'aufbau','Signallampe eingesteckt ?'),
(8,'aufbau','Erdung hergestellt ?'),
(9,'aufbau','Hauptschalter oder Schl&uuml;sselschalter (wenn vorhanden) auf AUS ?'),
(10,'aufbau','Winde frei von losen Teilen oder Verunreinigungen ?'),
(11,'aufbau','Bewegliche Teile (Rollen, Trommeln etc.) g&auml;ngig ?'),
(12,'aufbau','Hauptschalter jetzt eingeschaltet ?'),
(13,'aufbau','Kappvorrichtungen getestet ?'),
(14,'aufbau','Schleppseile richtig eingef&auml;delt (Umlenkrollen-F&uuml;hrung!) ?'),
(15,'aufbau','Vorseile/Seilfallschirm/Sollbruchstelle richtig montiert ?'),
(16,'aufbau','Hauptschalter oder Schl&uuml;sselschalter (wenn vorhanden) jetzt eingeschaltet ?'),
(17,'aufbau','Steuerpult-Anzeige (beide Trommeln) OK'),
(1,'abbau','Kappvorrichtungen entspannt bzw. gesichert?'),
(2,'abbau','Seilfallschirme; Vorseile, Kapphebel in Box verstauen'),
(3,'abbau','Lasten sicher verstaut?'),
(4,'abbau','Spriegelplanen richtig montiert (Seilspinnen!) ?'),
(5,'abbau','Anh&auml;nger korrekt angekuppelt (St&uuml;tzlast mind. 50kg, St&uuml;tzen & St&uuml;tzrad hoch, Abrißseil befestigt, Handbremse gel&ouml;t, el. Steckverbindung funktionsf&auml;hig)?'),
(6,'abbau','Handlungsbedarfe notiert (z.B. „Kappmesser wechseln“) ?'),
(1,'abstellen','Ladezustand der Batterie ?'),
(2,'abstellen','Hauptschalter aus ?'),
(3,'abstellen','Ladeger&auml;t angeschlossen / aktiviert ?  Bei 70% F&uuml;llstand nicht laden');

CREATE TABLE IF NOT EXISTS protocol (
	[protocol_id] integer primary key autoincrement,
	[winde_id] text not null,
	[pilot_id] text not null,
	[type] text not null,
	[kommentar] text null,
	[timestamp] datetime default current_timestamp,
	FOREIGN KEY(winde_id) REFERENCES winden(winde_id),
	FOREIGN KEY(pilot_id) REFERENCES piloten(pilot_id)
);

CREATE TABLE IF NOT EXISTS protocolanswers (
	[protocol_id] integer integer not null,
	[question] text not null, -- actual question text
	[answer] bit not null,
	FOREIGN KEY(protocol_id) REFERENCES protocol(protocol_id)
);