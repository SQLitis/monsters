
.. role:: bash(code)
   :language: bash

================
Monster Database
================

monsters.py merges XLS and SQLite data to make a searchable database.
All the data comes from other people; this is an automatic script rather than a one-shot conversion so that any later updates won't need my involvement to re-run the conversion.

Type :bash:`python monsters.py --help` for instructions on how to run the conversion.
`xlrd <https://github.com/python-excel/xlrd>`_ is required. As always, virtualenv.py is recommended before installing any Python module.

Here we are more concerned with what you can do after successfully running the conversion.
To run SQLite on the database, type :bash:`sqlite3 dnd_monsters.sqlite`.
Note that the old version of SQLite may not work, that is, :bash:`sqlite dnd_monsters.sqlite` will yield an error message "Unable to open database "dnd_monsters.sqlite": file is encrypted or is not a database".


-------------
Version notes
-------------
Each monster should now have a rulebook entry, but some monsters are in more than one rulebook, so maybe I should redesign this as an intersection table.

Right now I've just slapped in the names of the rulebooks only, no edition information or anything.
Some of the rulebook data will be obtained by cannibalizing `Hey I Can Chan's list <https://rpg.stackexchange.com/questions/1138/how-do-you-tell-if-a-dd-book-is-3-0-or-3-5>`_ or more accurately `Jackinthegreen's revision <http://www.minmaxboards.com/index.php?topic=15375.0>`_, but not all of them are included.

.. code-block:: bash

  CREATE TABLE "dnd_rulebook" (
  "dnd_edition_id" int(11) NOT NULL,
  "name" varchar(128) NOT NULL,
  "abbr" varchar(7) NOT NULL,
  "official_url" varchar(255) NOT NULL,
  "slug" varchar(128) NOT NULL,
  "published" date NOT NULL,




As a temporary hack, highmage's database is vendored in for psionic power data.


------------------
Using the database
------------------

Perhaps you've heard from Monsieur Meuble that humans and halflings are the only creatures in all of creation that cannot see in the dark.
We can check whether there are any creatures besides humans and halflings that have neither darkvision nor low-light vision.
We can immediately note that all types besides Humanoid give one of those automatically (yeah, yeah, except Ooze, that's a special case since they're all *blind*).

.. code-block:: bash

  sqlite> select dnd_monster.name from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id where dnd_monstertype.name="Humanoid" and not exists (select 1 from monster_special_ability inner join dnd_special_ability on monster_special_ability.special_ability_id=dnd_special_ability.id and monster_special_ability.monster_id=dnd_monster.id and (dnd_special_ability.name like "%darkvision%" or dnd_special_ability.name like "%low-light vision%") );


Which humanoids have the fastest movement speeds?

.. code-block:: bash

  sqlite> select abbrev,dnd_monster.name,speed,dnd_rulebook.name from dnd_monster inner join dnd_monstertype on type_id=dnd_monstertype.id and dnd_monstertype.name="Humanoid" inner join monster_movement_mode on dnd_monster.id=monster_id inner join (select abbrev as maxAbbrev,max(speed) as maxSpeed from dnd_monster inner join dnd_monstertype on dnd_monstertype.id=type_id inner join monster_movement_mode on dnd_monster.id=monster_id where dnd_monstertype.name="Humanoid" group by abbrev) on abbrev=maxAbbrev and speed=maxSpeed inner join dnd_rulebook on rulebook_id=dnd_rulebook.id;
  s|Selkie (seal form)|90|Fiend Folio
  b|Asherati|30|Sandstorm
  f|Phaethon|60|Key of Destiny
  f|Gargoyle, Mutant Four-Armed|60|Tomb of Horror
  c|Tasloi|40|Dragon Magazine
  f|Entomanothrope, Werewasp (giant wasp form)|60|Web

Hmm. The selkie and the asherati are great. But our flying and climbing winners might raise some eyebrows.

.. code-block:: bash

  sqlite> select abbrev,dnd_monster.name,speed,dnd_rulebook.name from dnd_monster inner join dnd_monstertype on type_id=dnd_monstertype.id and dnd_monstertype.name="Humanoid" inner join monster_movement_mode on dnd_monster.id=monster_id and (abbrev='c' or abbrev='f') inner join dnd_rulebook on rulebook_id=dnd_rulebook.id order by abbrev,speed;
  c|Goblin, Forestkith|20|Monster Manual III
  c|Goblin, Snow|20|Frostburn
  c|Tasloi|20|Shining South
  c|O'bati|20|Web
  c|Vanara|20|Web
  c|Spirit Folk, Mountain|30|Unapproachable East
  f|Imago|40|Savage Species (Web Enhancement)
  f|Saurial, Flyer|50|Serpent Kingdoms

Since almost all monsters have a land speed, I went ahead and incorporated that in the main table, so that's a little easier to access.

.. code-block:: bash

  sqlite> select dnd_monster.name,land_speed,dnd_rulebook.name from dnd_monster inner join dnd_monstertype on type_id=dnd_monstertype.id and dnd_monstertype.name="Humanoid" inner join dnd_rulebook on rulebook_id=dnd_rulebook.id order by land_speed;
  Varag|60|Monster Manual IV



Suppose you noticed that creatures with gaze attacks can be safely viewed in mirrors.
`Looking at the creature's image (such as in a mirror) does not subject the viewer to a gaze attack. <http://www.d20srd.org/srd/specialAbilities.htm#gazeAttacks>`_
That seems like quite the loophole. But wait: `vampires throw no reflections in mirrors. <http://www.d20srd.org/srd/monsters/vampire.htm>`_

Are there vampires with gaze attacks? Obviously all vampires have their Dominate Person gaze attack, but aside from that.

.. code-block:: bash

  $ sqlite3 dnd_monsters.sqlite
  sqlite> select dnd_monster.name,dnd_special_ability.name from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join monster_special_ability on dnd_monster.id=monster_id inner join dnd_special_ability on dnd_special_ability.id=special_ability_id where (dnd_monstertype.name="Humanoid" or dnd_monstertype.name="Monstrous Humanoid") and dnd_special_ability.name like "%gaze%";
  Medusa|Petrifying gaze
  Gloom|Fear gaze
  Hebi-no-onna|Hypnotic gaze
  Xtabay|witching gaze
  Blindheim|Gaze

But this misses the sea hag, so we're probably missing others. Maybe try a few more gaze-sounding keywords?

.. code-block:: bash

  sqlite> select dnd_monster.name,dnd_special_ability.name from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join monster_special_ability on dnd_monster.id=monster_id inner join dnd_special_ability on dnd_special_ability.id=special_ability_id where (dnd_monstertype.name="Humanoid" or dnd_monstertype.name="Monstrous Humanoid") and (dnd_special_ability.name like "%gaze%" or dnd_special_ability.name like "%eye%" or dnd_special_ability.name like "%appearance%");
  Hag, Sea Hag|Evil eye
  Hag, Sea Hag|horrific appearance
  Medusa|Petrifying gaze
  Gloom|Fear gaze
  Hag, Marzanna|Dreadful eye
  Hebi-no-onna|Hypnotic gaze
  Xtabay|witching gaze
  Blindheim|Gaze

This correctly catches the sea hag's Evil Eye, but incorrectly catches the sea hag's horrific appearance. (A sea hag's horrific appearance is not treated as a gaze attack per se; in particular, it is just as effective when the sea hag is viewed in a mirror, so it's not an example of what we were originally looking for.)
And we're still probably missing a lot. In particular, the vampire's own Dominate ability doesn't have any hint in the name that it's a gaze attack; to know that, we have to look at the description. As far as I know, that data is not currently available in any convenient format; *I'm* certainly not going to make it.

*Spell-like* abilities, however, are standardized. Indeed the entire *point* of spell-like abilities, from the game designers' perspective, is to be standardized: they don't have to come up with exactly how a given ability works from scratch.
This is also very handy when searching.

There *are* existing sources letting us match spell names to spell metadata.

To use this tool, you will need an existing SQLite database with, at minimum, the following tables: dnd_spell, dnd_spellschool, dnd_racesize, dnd_monstertype, dnd_rulebook.

.. code-block:: bash

  sqlite> select distinct dnd_spellclasslevel.level,dnd_spell.name,dnd_monsters.name,hit_dice from monster_spell_like_abilities inner join dnd_monsters on monster_spell_like_abilities.monster_id=dnd_monsters.id inner join dnd_spell on dnd_spell.id=monster_spell_like_abilities.spell_id inner join dnd_spellclasslevel on dnd_spell.id=dnd_spellclasslevel.spell_id inner join dnd_monstertype on dnd_monstertype.id=dnd_monsters.type_id where (dnd_monstertype.name="Undead") and hit_dice<=5 order by dnd_spellclasslevel.level,hit_dice;
  2|Suggestion|Brain in a Jar|3
  2|Ghoul Glyph|Deathlock|3
  2|Invisibility|Gaki, Jiki-niku-gaki|3
  3|Haste|Time Wight|5
  3|Slow|Time Wight|5
  4|Dominate Person|Brain in a Jar|3
  5|Telekinesis|Brain in a Jar|3
  5|Dominate Person|Brain in a Jar|3
  5|Passwall|Gaki, Jiki-niku-gaki|3

A 6th-level cleric can enslave a `Brain in a Jar <http://archive.wizards.com/default.asp?x=dnd/iw/20041015b&page=2>`_, while the same cleric with the Improved Turning feat and a Scepter of the Netherworld can master a `Time Wight <http://archive.wizards.com/default.asp?x=dnd/mm/20030620a>`_.



Hmm. Are there monsters that can pull similar tricks?
Since the database currently lacks the full text of abilities, we cannot search for "as an evil cleric rebukes undead" or such, but we can poke around with names.

.. code-block:: bash

  sqlite> select dnd_monster.name,dnd_special_ability.name from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join monster_special_ability on dnd_monster.id=monster_id inner join dnd_special_ability on dnd_special_ability.id=special_ability_id where (dnd_special_ability.name like "%rebuke%" or dnd_special_ability.name like "%control%" or dnd_special_ability.name like "%command%");
  Earth Whisper|control earth creatures

An earth whisper, as it turns out, commands earth creatures as an evil cleric commands undead. What's available?

.. code-block:: bash

  sqlite> select distinct dnd_monster.name,hit_dice,dnd_rulebook.name from dnd_monster inner join monster_has_subtype on dnd_monster.id=monster_has_subtype.monster_id inner join dnd_monstersubtype on monster_has_subtype.subtype_id=dnd_monstersubtype.id inner join dnd_rulebook on rulebook_id=dnd_rulebook.id where (dnd_monstersubtype.name="Earth") and hit_dice<=2 order by hit_dice;
  Gen, Earth|1|Dragon Magazine
  Elemental, Earth, Small|2
  Paraelemental, Magma, Small|2
  Paraelemental, Ooze, Small|2
  Stonechild|2|Miniatures Handbook

Earth whispers can advance in hit dice, or can be granted bonus hit dice by a bard. If we allow the hit dice to go a little higher, what spell-like abilities show up?

.. code-block:: bash

  sqlite> select distinct dnd_spellclasslevel.level,dnd_spell.name,dnd_monster.name,hit_dice from monster_has_spell_like_ability inner join dnd_monster on monster_has_spell_like_ability.monster_id=dnd_monster.id inner join dnd_spell on dnd_spell.id=monster_has_spell_like_ability.spell_id inner join dnd_spellclasslevel on dnd_spell.id=dnd_spellclasslevel.spell_id inner join monster_has_subtype on dnd_monster.id=monster_has_subtype.monster_id inner join dnd_monstersubtype on monster_has_subtype.subtype_id=dnd_monstersubtype.id where (dnd_monstersubtype.name="Earth") and hit_dice<=3 order by hit_dice,dnd_spellclasslevel.level;
  2|Soften Earth and Stone|Mephit, Earth|3
  2|Glitterdust|Mephit, Salt|3
  3|Stinking Cloud|Mephit, Sulfur|3



Say, looking for Earth subtypes made me wonder: Elemental's good saves depend on the element: Fortitude (earth, water) or Reflex (air, fire). What about elementals that aren't earth, water, air, or fire? Are there any?

.. code-block:: bash

  sqlite> select dnd_monster.name,dnd_rulebook.name from dnd_monster inner join (select distinct dnd_monster.id as monsterID from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id where dnd_monstertype.name="Elemental" except select distinct dnd_monster.id from dnd_monster inner join monster_has_subtype on dnd_monster.id=monster_has_subtype.monster_id inner join dnd_monstersubtype on monster_has_subtype.subtype_id=dnd_monstersubtype.id where (dnd_monstersubtype.name="Earth" or dnd_monstersubtype.name="Fire" or dnd_monstersubtype.name="Air" or dnd_monstersubtype.name="Water") ) on dnd_monster.id=monsterID inner join dnd_rulebook on dnd_monster.rulebook_id=dnd_rulebook.id;
  Chraal|Monster Manual III
  Elemental, Taint, Small|Heroes of Horror
  Elemental, Shadow, Small|Tome of Magic
  Cryonax (Prince of Evil Cold Creatures, Bringer of Endless Winter, The Bleak Monarch)|Dragon Magazine

As it turns out, the (Cold) Chraals are native to the Elemental Plane of Water, and not the Elemental Plane of Air, so they follow the rule for water elementals.
The (Evil) taint elementals also follow the earth/water rule, possibly because their forms are constantly in flux, flowing like a viscous liquid.
The (Incorporeal) shadow elementals follow the air rule.
The (Cold, Evil) Cryonax surprisingly follows the air rule.


We can search for monsters by home plane.

.. code-block:: bash

  sqlite> select dnd_monster.name,dnd_rulebook.name from dnd_monster inner join monster_on_plane on dnd_monster.id=monster_on_plane.monster_id inner join dnd_plane on (plane_id=dnd_plane.id or plane_id=dnd_plane.parent_plane) inner join dnd_rulebook on rulebook_id=dnd_rulebook.id where dnd_plane.name="Thuldanin";

The clause :bash:`plane_id=dnd_plane.id or plane_id=dnd_plane.parent_plane` means that if a monster is listed (plane_id) as being native to Acheron (parent_plane) as a whole, rather than Thuldanin specifically, we still want it to show up in our results, since it can be found in Thuldanin.

But what if we want the results to list which layer each monster hails from? For that, we need something a little more complicated.

.. code-block:: bash

  sqlite> select dnd_monster.name,dnd_plane.name,dnd_rulebook.name from dnd_monster inner join monster_on_plane on dnd_monster.id=monster_on_plane.monster_id inner join dnd_plane on plane_id=dnd_plane.id left join (select parent_plane as planeID, name as layerName from dnd_plane) on plane_id=planeID inner join dnd_rulebook on rulebook_id=dnd_rulebook.id where (dnd_plane.name="Thuldanin" or layerName="Thuldanin");

The inner join with dnd_plane gets us the actual planar name listed in the monster's entry.
We then do a separate left join so that, if the monster is listed for Acheron as a whole, we will still get the layerName Thuldanin to match against.


Let's assume we don't know yet which layer we want, we're just trying to get a sense of what lives in Acheron.
So we want to show all the layers, but our results should correctly list the name of the layer each monster lives on.

.. code-block:: bash

  sqlite> select dnd_monster.name,dnd_plane.name,dnd_rulebook.name from dnd_monster inner join dnd_rulebook on rulebook_id=dnd_rulebook.id inner join monster_on_plane on dnd_monster.id=monster_on_plane.monster_id inner join dnd_plane on plane_id=dnd_plane.id left join (select id as parentID, name as parentName from dnd_plane) on parent_plane=parentID where (dnd_plane.name="Acheron" or parentName="Acheron");

As you can see, this is pretty clunky, so for now entries have been inserted into the table placing everything listed as Thuldanin also for Acheron.


.. As a general rule, natural joins are a bad choice in the long term. You might store such queries in stored procedures, triggers, or applications. Then someone modifies the table structure --- adds, removes, or renames a column. And, the code stops working.


Let's do something complicated.
Suppose that you have fallen into a gate to Phlegethos that unexpectedly opened in the town of Brindinford.
Unfortunately, Phlegethos tends to burn people to ash. As soon as your magical protections run out, you're going to die. Fortunately, the two neighboring layers, Stygia and Minauros, don't do that. Stygia would be easier to get to, but in the long term that's getting you further from safety, so it would be better to go up to Minauros.
Unfortunately, you can't fly. Fortunately, you are an adventurer! You can beat down a devil and force it to fly you up to Minauros! Just don't go all scorpion-and-the-frog on it and stab it while it's carrying you.

But pity the poor DM. Can you do that? What even lives in Phlegethos, anyway?

There doesn't seem to be a staircase from Phlegethos to Minauros. Most traffic probably is by flying. Come to think of it, how do they ferry Baatorian greensteel up from Phlegethos? Who carries it?

.. code-block:: bash

  sqlite> select distinct challenge_rating, dnd_monster.name, 2640/(speed*max_up_per_move*4), dnd_racesize.name, fine_biped_max_load_ounces*biped_carry_factor/3/16, dnd_rulebook.name from dnd_monster inner join monster_on_plane on dnd_monster.id=monster_on_plane.monster_id inner join dnd_plane on (plane_id=dnd_plane.id or plane_id=dnd_plane.parent_plane) inner join monster_movement_mode on dnd_monster.id=monster_movement_mode.monster_id and abbrev='f' inner join monster_maneuverability on monster_maneuverability.monster_id=dnd_monster.id inner join dnd_maneuverability on monster_maneuverability.maneuverability=dnd_maneuverability.maneuverability inner join dnd_racesize on size_id=dnd_racesize.id natural join carrying_capacity inner join dnd_rulebook on rulebook_id=dnd_rulebook.id where dnd_plane.name like "%phlegethos%" and challenge_rating<=10 order by speed*max_up_per_move;
  6|Devil, Kocrachon|34.7017059221718|Medium|76|Book of Vile Darkness
  7|Devil, Amnizu|34.7017059221718|Medium|43|Fiendish Codex 2
  3|Devil, Advespa|33.0|Large|266|Monster Manual II
  8|Devil, Erinyes|26.4|Medium|153|Monster Manual
  4|Devil, Spined (Spinagon)|17.3508529610859|Small|25|Fiendish Codex 2
  8|Bloodcurdle (The Hag Countess's Nightmare)|14.6666666666667|Huge|1226|Book of Vile Darkness
  2|Devil, Imp|13.2|Tiny|16|Monster Manual
  3|Devil, Imp, Euphoric|13.2|Tiny|16|Fiend Folio

2640/(speed*max_up_per_move*4) is the number of rounds it would take for the monster to ascend a half-mile while running. Generally, a character can run for a minute or two before having to rest for a minute, so this works as a first approximation.
max_up_per_move is obtained by looking at the monster's fly speed and maneuverability (and thus maximum up-angle). We'll guess most monsters don't have the Run feat, so we multiply by 4 to get how far it goes in a round.

fine_biped_max_load_ounces*biped_carry_factor is the monster's maximum load. A creature with a fly speed can move through the air at the indicated speed if carrying no more than a light load. A light load is always exactly one-third of the corresponding maximum load, so we divide by 3. This is in ounces, so if we want pounds we divide by 16.

The unsurprising winner for speed is the humble imp. If you remembered to pack your scroll of Reduce Person, and you remembered to put ranks in Use Magic Device, and you weigh less than 128 pounds, an imp can carry you up. And your party said you'd never use that thing!

If you forgot your scroll of Reduce Person, well, then you're in trouble. Stealing the Hag Countess's Nightmare seems like a poor idea. An erinyes is half as fast as an imp, and can probably carry you...but notice that Challenge Rating of 8. An erinyes is pretty tough.
The advespa, on the other hand, can easily carry you and your gear. Running for 3.3 minutes without a break is a stretch, but even if the trip ends up taking five minutes or so, you'll probably be okay, provided that you're lucky enough to stumble across a lone advespa soon after arriving.





For one adventure, I wanted to have a set of seven otherworldly "living wells".

.. code-block:: bash

  sqlite> select distinct dnd_monster.name,challenge_rating from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join monster_has_subtype on dnd_monster.id=monster_has_subtype.monster_id inner join dnd_monstersubtype on monster_has_subtype.subtype_id=dnd_monstersubtype.id where (dnd_monstertype.name="Outsider" or dnd_monstertype.name="Elemental") and (dnd_monstersubtype.name="Water" or dnd_monstersubtype.name="Aquatic") order by challenge_rating;
  Gen, Water|-2
  Paraelemental, Ooze, Small|1
  Imp, Vapor|1
  Elemental, Ectoplasm, Small|1
  Elemental Grue, Vardigg|2
  Elemental Steward, Arctine|2
  Mephit, Ooze|3
  Mephit, Water|3
  Tojanida, Juvenile|3
  Paraelemental, Ooze, Medium|3
  Elemental, Ectoplasm, Medium|3
  Demon, Skulvyn|4
  Demon, Elemental, Water|4
  Tojanida, Adult|5
  Paraelemental, Ooze, Large|5
  Orlythys|5
  Elemental Weird, Water, Lesser|5
  Elemental, Ectoplasm, Large|5
  Spawn of Juiblex, Lesser|6
  Elemental Spawn, Acid|6
  Elemental Spawn, Mist|6
  Elemental Spawn, Mud|6
  Paraelemental, Ooze, Huge|7
  Elemental, Ectoplasm, Huge|7
  Yugoloth, Echinoloth|8
  Tojanida, Elder|9
  Immoth|9
  Aspect of Dagon|9
  Genie, Marid|9
  Paraelemental, Ooze, Greater|9
  Caller from the Deeps|9
  Elemental, Ectoplasm, Greater|9
  Spawn of Juiblex, Greater|10
  Paraelemental, Ooze, Elder|11
  Elemental, Ectoplasm, Elder|11
  Elemental Weird, Water|12
  Aspect of Sekolah|13
  Scyllan|13
  Spawn of Juiblex, Elder|14
  Omnimental|15
  Avatar of Elemental Evil, Waterveiled Assassin|15
  Elemental Weird, Ice|15
  Tempest|16
  Demon, Uzollru|16
  Elemental, Water, Monolith|17
  Demon, Wastrilith|17
  Paraelemental, Ooze, Monolith|17
  Demon, Myrmyxicus|21
  Dagon (Prince of the Depths)|22
  Olhydra (Princess of Evil Water Creatures, Princess of Watery Evil, Mistress of the Black Tide)|22
  Ben-hadar (Prince of Good Water Creatures, Squallbringer, The Valorous Tempest)|22
  Essence of Shothragot|22
  Demogorgon (Prince of Demons)|23

Here we can see that a water gen is listed as CR -2...huh?
To keep the size down, fractions of the form 1/x are stored as negative integers.
-2 means 1/2.


Suppose we start thinking about what demons might use Extract Gift to keep tabs on a number of mortals.
The classic imp-like quasit actually does not have telepathy.
(However, Extract Gift itself gives telepathy, but let's say for flavor consistency we want the demon to be telepathic before the Extract Gift ritual.)

.. code-block:: bash

  sqlite> select distinct dnd_monster.name,challenge_rating,intelligence,dnd_special_ability.name from dnd_monster inner join monster_special_ability on dnd_monster.id=monster_special_ability.monster_id inner join dnd_special_ability on monster_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id left join monster_subtype on dnd_monster.id=monster_subtype.monster_id left join dnd_monstersubtype on monster_subtype.subtype_id=dnd_monstersubtype.id where (dnd_monster.name like "Demon, %") and (dnd_monstersubtype.name="Tanar'ri" or dnd_special_ability.name like "%telepathy%") order by (challenge_rating);
  Demon, Mane|1|3|Acidic cloud
  Demon, Dretch|2|5|summon tanar'ri
  Demon, Gadacro|3|8|Eyethief
  Demon, Rutterkin|3|9|summon tanar'ri
  Demon, Incubus|3|14|SLAs
  Demon, Incubus|3|14|Wisdom damage
  Demon, Bogannarr|4|8|summon tanar'ri
  Demon, Jovoc|5|7|summon tanar'ri
  Demon, Bar-lgura|5|13|Abduction
  Demon, Nabassu, Juvenile|5|14|Sneak attack +2d6
  Demon, Skurchur|5|15|touch of vacant beauty
  Demon, Babau|6|14|Sneak attack +2d6
  Demon, Uridezu|6|8|rat empathy
  Demon, Artaaglith|6|13|spells (clr5)

Note the left join for subtypes, because it's technically possible that a demon might not have a subtype (though very unlikely and it would mean a splatbook was doing something weird or a data-entry error).

What monsters have innate bardic music?

.. code-block:: bash

  sqlite> select distinct dnd_monster.name,dnd_monstertype.name,hit_dice,dnd_special_ability.name from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id where dnd_special_ability.name like "%music%";
  Lillend|Outsider|7|Bardic music (brd6)
  Orc, War Howler|Humanoid|4|Bardic music (brd2)
  Ruin Chanter|Fey|20|Bardic music (brd12)
  Morwel (Queen of Stars) (humanoid form)|Outsider|39|Bardic music (brd20)
  Morwel (Queen of Stars) (globe form)|Outsider|39|Bardic music (brd20)
  Faerinaal (The Queen's Consort) (humanoid form)|Outsider|32|Bardic music
  Faerinaal (The Queen's Consort) (globe form)|Outsider|32|Bardic music
  Eladrin, Tulani (humanoid form)|Outsider|18|Bardic music (brd18)
  Drow, Szarkai Provocateur|Humanoid|12|Bardic music (brd7)
  Spectral Lyrist|Undead|6|Bardic music




On a lighter note, I always thought that a "living will" sounded like a magical incorporeal construct. Say, are there any incorporeal constructs?

.. code-block:: bash

  sqlite> select distinct dnd_monster.name,challenge_rating from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join monster_subtype on dnd_monster.id=monster_subtype.monster_id inner join dnd_monstersubtype on monster_subtype.subtype_id=dnd_monstersubtype.id where (dnd_monstertype.name="Construct") and (dnd_monstersubtype.name="Incorporeal") order by challenge_rating;
  Umbral Spy|3
  Golem, Prismatic|18




