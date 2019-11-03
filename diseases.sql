CREATE TABLE disease_transmission (
  id char(1) PRIMARY KEY
  ,name char(8) NOT NULL
);
INSERT INTO disease_transmission (id, name) VALUES ('C', 'Contact'), ('S', 'Special'), ('B', 'Injury'), ('H', 'Ingested'), ('M', 'Inhaled');

CREATE TABLE disease (
  id INTEGER PRIMARY KEY
  ,name TEXT
  ,rulebook_id INTEGER NOT NULL
  ,infection_id char(1) NOT NULL
,FOREIGN KEY(rulebook_id) REFERENCES dnd_rulebook(id)
,FOREIGN KEY(infection_id) REFERENCES disease_transmission(id)
);
CREATE TEMPORARY TABLE tmpDisease (name TEXT, rulebook_abbrev TEXT, infection_id char(1), FOREIGN KEY(infection_id) REFERENCES disease_transmission(id));
INSERT INTO tmpDisease (name, rulebook_abbrev, infection_id) VALUES ('Acid fever', 'BoVD', 'B')
  ,('Blue guts', 'BoVD', 'S')
  ,('Deathsong', 'BoVD', 'C')
  ,('Faceless hate', 'BoVD', 'B')
  ,('Festering anger', 'BoVD', 'S')
  ,('Fire taint', 'BoVD', 'M')
  ,('Frigid ravaging', 'BoVD', 'B')
  ,('Iron corruption', 'BoVD', 'B')
  ,('Life blindness', 'BoVD', 'M')
  ,('Lightning curse', 'BoVD', 'C')
  ,('Melting fury', 'BoVD', 'C')
  ,('Misery''s passage', 'BoVD', 'B')
  ,('Possession infection', 'BoVD', 'C')
  ,('Sound sickness', 'BoVD', 'C')
  ,('Soul rot', 'BoVD', 'S')
  ,('Vile rigidity', 'BoVD', 'C')
  ,('Warp touch', 'BoVD', 'C')
  ,('Flesh-Eating Bacillus', 'LM', 'C')
  ,('Blood Fever', 'HoH', 'C')
  ,('Darklight ore poisoning', 'DotU', 'C')
  ,('Blinding sickness', 'DMG', 'H')
  ,('Cackle fever', 'DMG', 'M')
  ,('Demon fever', 'DMG', 'B')
  ,('Devil chills', 'DMG', 'B')
  ,('Filth fever', 'DMG', 'B')
  ,('Mindfire', 'DMG', 'M')
  ,('Mummy rot', 'DMG', 'C')
  ,('Red ache', 'DMG', 'B')
  ,('Shakes', 'DMG', 'C')
  ,('Slimy doom', 'DMG', 'C')
  ,('Eternal torpor', 'BoED', 'C')
  ,('Consuming passion', 'BoED', 'C')
  ,('Depraved decadence', 'BoED', 'H')
  ,('Pride in vain', 'BoED', 'H')
  ,('Raging desire', 'BoED', 'M')
  ,('Haunting conscience', 'BoED', 'M')
  ;
INSERT INTO disease (name, rulebook_id, infection_id) SELECT name, rulebook_id, infection_id FROM tmpDisease LEFT JOIN rulebook_abbrev ON rulebook_abbrev.abbr=tmpDisease.rulebook_abbrev;
DROP TABLE tmpDisease;
