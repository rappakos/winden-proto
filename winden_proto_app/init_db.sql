
--DROP TABLE flying_days;
CREATE TABLE IF NOT EXISTS flying_days (
	[flying_day] DATE NOT NULL 
			CONSTRAINT CHK_flying_day CHECK (flying_day==strftime('%Y-%m-%d',flying_day)),
	[pilot_list] BIT NOT NULL DEFAULT 0,
	[active_winde_id] TEXT NULL, -- FK
	[winde_aufgebaut] BIT NOT NULL DEFAULT 0,
	[winde_abgebaut] BIT NOT NULL DEFAULT 0,
	[active_wf] TEXT NULL,
	[canceled] BIT NOT NULL DEFAULT 0,
	[create_timestamp] datetime not null default current_timestamp
);



/* OLD SCHEMA : */

CREATE TABLE IF NOT EXISTS piloten (
	pilot_id TEXT NOT NULL UNIQUE PRIMARY KEY,
	[name] TEXT NOT NULL,
	[status_txt] TEXT NOT NULL, -- could be FK to status 
    [zugkraft] int null,
	verein TEXT NULL
);

INSERT OR IGNORE INTO piloten (pilot_id,[name] ,[status_txt])
VALUES
('Akos','Akos','W')
,('Orsi','Orsi','W')
,('Helmut','Helmut','EWF')
,('Michi','Michi','EWF')
,('Beate','Beate','M')
,('Martin','Martin','M')
,('Tommi','Tommi','NG')
,('Markus','Markus','G');

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

--DROP TABLE schlepps; -- reset

CREATE TABLE IF NOT EXISTS schlepps (
			[schlepp_id] integer primary key autoincrement,
	     	[winde_id] text not null,
            [wf_id] text not null,
            [ewf_id] text null,
            [pilot_id]  text not null,
            [datum] text not null, -- ISO YYYY-MM-DD
            [status] text not null default 'started',
            [schlepp_start] datetime default current_timestamp,
            [status_date] datetime default current_timestamp,
			FOREIGN KEY(winde_id) REFERENCES winden(winde_id)
			FOREIGN KEY(wf_id) REFERENCES piloten(pilot_id)
			FOREIGN KEY(pilot_id) REFERENCES piloten(pilot_id)
);

CREATE TABLE IF NOT EXISTS protocolquestions (
	[id] integer primary key autoincrement,
	[question_id] integer not null,
	[type] text not null, -- aufbau / abbau
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

--DROP TABLE protocol;

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