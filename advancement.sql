CREATE TABLE advancement_size_increase (
  new_size_id INTEGER NOT NULL
  ,strength_increase tinyint(1) NOT NULL
  ,FOREIGN KEY (new_size_id) REFERENCES dnd_racesize(id)
  );
CREATE TEMPORARY TABLE tmpAdvancementSize (size_name TEXT, strength_increase tinyint(1));
INSERT INTO tmpAdvancementSize (size_name, strength_increase) VALUES ("Diminutive", 0)
  ,("Tiny", 2)
  ,("Small", 4)
  ,("Medium", 4)
  ,("Large", 8)
  ,("Huge", 8)
  ,("Gargantuan", 8)
  ,("Colossal", 8)
  ;
INSERT INTO advancement_size_increase (new_size_id, strength_increase) SELECT dnd_racesize.id, strength_increase FROM tmpAdvancementSize INNER JOIN dnd_racesize ON dnd_racesize.name=size_name;
DROP TABLE tmpAdvancementSize;
