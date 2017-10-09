
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

In a similar vein, we can check whether all Outsiders are coded as either Native or Extraplanar. It turns out there are a few that are neither, but not many, mostly old ones.

.. code-block:: bash

  sqlite> select dnd_monster.name,dnd_rulebook.name from dnd_monster inner join (select distinct dnd_monster.id as monsterID from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id where dnd_monstertype.name="Outsider" except select distinct dnd_monster.id from dnd_monster inner join monster_has_subtype on dnd_monster.id=monster_has_subtype.monster_id inner join dnd_monstersubtype on monster_has_subtype.subtype_id=dnd_monstersubtype.id where (dnd_monstersubtype.name="Extraplanar" or dnd_monstersubtype.name="Native") ) on dnd_monster.id=monsterID inner join dnd_rulebook on dnd_monster.rulebook_id=dnd_rulebook.id;


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


.. code-block:: bash

  sqlite> select distinct dnd_special_ability.name, dnd_monster.name, dnd_rulebook.name, hit_dice from dnd_monster inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id left join monster_has_subtype on dnd_monster.id=monster_has_subtype.monster_id left join dnd_monstersubtype on subtype_id=dnd_monstersubtype.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where dnd_monstertype.name="Animal" and (dnd_monstersubtype.name is null or dnd_monstersubtype.name!="Swarm") and dnd_special_ability.name not like "%resistan%" and dnd_special_ability.name not like "%saves vs. spells%" and dnd_special_ability.name not like "immun%" and dnd_special_ability.name not like "disease%" and dnd_special_ability.name not like "%powerful%" and dnd_special_ability.name not like "double damage %" and dnd_special_ability.name!="Augmented critical" and dnd_special_ability.name!="Evasion" and dnd_special_ability.name!="uncanny dodge" and dnd_special_ability.name not like "%trample%" and dnd_special_ability.name!="stampede" and dnd_special_ability.name not like "rake %" and dnd_special_ability.name not like "rend 2d%" and dnd_special_ability.name not like "constrict %" and dnd_special_ability.name not like "swallow whole" and dnd_special_ability.name not like "coil slam 1d%" and dnd_special_ability.name not like "%tail sweep%" and dnd_special_ability.name not like "%Frenzy" and dnd_special_ability.name not like "rage" and dnd_special_ability.name != "Ferocity" and dnd_special_ability.name!="Damage Reduction" and dnd_special_ability.name!="Low-Light Vision" and dnd_special_ability.name!="Darkvision" and dnd_special_ability.name!="light sensitivity" and dnd_special_ability.name not like "%scent" and dnd_special_ability.name not like "improved grab"and dnd_special_ability.name not like "trip" and dnd_special_ability.name not like "pounce" and dnd_special_ability.name not like "blinds%" and dnd_special_ability.name not like "tremorsense %" and dnd_special_ability.name not like "hold breath" and dnd_special_ability.name not like "poison%" and dnd_special_ability.name not like "venom%" and dnd_special_ability.name!="blood drain" order by hit_dice;
  sprint|Cheetah|Monster Manual|3
  Fast Healing|Snake, Glacier|Serpent Kingdoms|2
  Wounding|Bat, Guard|Monster Manual II|4
  Acid spit|Dragon Newt|Web|1 Spit (Ex): The dragon newt can spit acidic globules with a range increment of 10 feet. This is a ranged touch attack that deals 1d4 points of acid damage.
  Acidic bite|Titan Salamander|Web|4 Acidic Bite (Ex): The titan salamander's saliva is caustic and inflicts 1d6 points of additional acid damage on a successful bite attack. http://archive.wizards.com/default.asp?x=dnd/mm/20030920a
  Blood squirt|Dinosaur, Bloodstriker|Monster Manual III|9

.. code-block:: bash

  sqlite> select distinct dnd_special_ability.name, dnd_monster.name, dnd_rulebook.name, max(0,hit_dice) + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id left join monster_has_subtype on dnd_monster.id=monster_has_subtype.monster_id left join dnd_monstersubtype on subtype_id=dnd_monstersubtype.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstertype.name="Animal" or (dnd_monstertype.name="Magical Beast" and intelligence<3) ) and (dnd_monstersubtype.name is null or dnd_monstersubtype.name!="Swarm") and dnd_special_ability.name not like "%resistan%" and dnd_special_ability.name not like "%saves vs. spells%" and dnd_special_ability.name not like "immun%" and dnd_special_ability.name not like "disease%" and dnd_special_ability.name not like "%powerful%" and dnd_special_ability.name not like "double damage %" and dnd_special_ability.name!="Augmented critical" and dnd_special_ability.name!="Evasion" and dnd_special_ability.name!="uncanny dodge" and dnd_special_ability.name not like "%trample%" and dnd_special_ability.name!="stampede" and dnd_special_ability.name not like "rake %" and dnd_special_ability.name not like "rend 2d%" and dnd_special_ability.name not like "constrict %" and dnd_special_ability.name not like "swallow whole" and dnd_special_ability.name not like "coil slam 1d%" and dnd_special_ability.name not like "%tail sweep%" and dnd_special_ability.name not like "%Frenzy" and dnd_special_ability.name not like "rage" and dnd_special_ability.name != "Ferocity" and dnd_special_ability.name!="Damage Reduction" and dnd_special_ability.name!="Low-Light Vision" and dnd_special_ability.name!="Darkvision" and dnd_special_ability.name!="light sensitivity" and dnd_special_ability.name not like "%scent" and dnd_special_ability.name not like "improved grab"and dnd_special_ability.name not like "trip" and dnd_special_ability.name not like "pounce" and dnd_special_ability.name not like "blinds%" and dnd_special_ability.name not like "tremorsense %" and dnd_special_ability.name not like "hold breath" and dnd_special_ability.name not like "poison%" and dnd_special_ability.name not like "venom%" and dnd_special_ability.name!="blood drain" and dnd_monster.name not like "%hydra, %" order by -DC;
  Chill darkness|Skiurid|Monster Manual IV|-2
  shadow jump|Skiurid|Monster Manual IV|-2
  Flame spit|Ash Rat|Monster Manual II|1
  Color spray|Corollax|Monster Manual II|1
  Elysian song|Elysian Thrush|Planar Handbook|6
  quills|Deaglu|Garden of the Plantmaster|6
  Sonic ray|Thrum Worm|Races of Stone|7
  Magic missile|Phase Wasp|Monster Manual II|7
  stunning shock|Shocker Lizard|Monster Manual|7
  quills|Quillflinger|Web|8 http://archive.wizards.com/default.asp?x=dnd/mm/20020215a
  PLAs|Chekryan|Sandstorm|8 Dimension Door can take along one Medium creature
  silence|Rothé, Ghost|Forgotten Realms Campaign Setting|9
  Breath weapon 3d6 fire every 1d4 rounds|Horned Beast|Tome of Magic|9
  Growth|Blood Ape|Monster Manual II|9 the ability to return to Large size means that blood apes require substantially less food than Huge creatures would.
  Petrification|Cockatrice|Monster Manual|10
  Petrifying gaze|Basilisk|Monster Manual|11
  Controlling sting|Quanlos|Monster Manual IV|11
  Reverse gravity|Gravorg|Monster Manual II|15
  Plane shift|Gaspar|Planar Handbook|19
  Trill|Frost Worm|Monster Manual|19


.. code-block:: bash

  sqlite> select distinct dnd_special_ability.name, (hit_dice*3/4 + (strength - 10)/2 + (size_id - 5)*4), dnd_monstertype.name, dnd_racesize.name, strength, dnd_monster.name, dnd_rulebook.name, hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstertype.name="Animal" or (dnd_monstertype.name="Magical Beast" and intelligence<3) ) and dnd_special_ability.name like "%improved grab%" order by (hit_dice*3/4 + strength/2 + size_id*4), -DC, -size_id;
  improved grab|24|Large|27|Snake, Legendary|Monster Manual II|16
  Improved grab|30|Huge|34|Woolly Mammoth|Frostburn|14
  Improved grab|34|Large|33|Tiger, Legendary|Monster Manual II|26
  Improved grab|35|Huge|39|Bear, Polar, Dire|Frostburn|18
  Improved grab|36|Gargantuan|34|Dinosaur, Plesiosaur|Stormwrack|16
  improved grab|40|Gargantuan|36|Dinosaur, Spinosaurus|Monster Manual II|20
  Improved grab|43|Gargantuan|37|Toad, Titanic Mutant|Return to the Temple of the Frog|25
  Improved grab|51|Huge|42|Dinosaur, Battletitan|Monster Manual III|36
  improved grab|62|Colossal|46|Dinosaur, Liopleurodon|Dragon Magazine|38

Interestingly, if we restrict to Large or smaller, there are no reversals; all Large are better grapplers than all Medium-size are better grapplers than all Small.

.. code-block:: bash

  sqlite> select distinct dnd_special_ability.name, (hit_dice*3/4 + (strength - 10)/2 + (size_id - 5)*4), dnd_racesize.name, strength, dnd_monster.name, dnd_rulebook.name, hit_dice from dnd_monster inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where dnd_monstertype.name="Animal" and size_id<=6 and dnd_special_ability.name like "%improved grab%" order by (hit_dice*3/4 + strength/2 + size_id*4), -hit_dice;
  Improved grab|0|Small|16|Lynx|Dangerous Denizens - The Monsters of Tellene|2
  Improved grab|6|Medium|19|Crocodile|Monster Manual|3
  Improved grab|6|Medium|18|Puma (Cougar, Mountain Lion)|Dangerous Denizens - The Monsters of Tellene|3
  improved grab|6|Medium|19|Komodo Dragon|Dragon Magazine|3
  Improved grab|7|Medium|19|Thudhunter|Arms & Equipment Guide|4 Thudhunter young are worth 200 gp on the open market.
  Improved grab|7|Medium|18|Jaguar|Dangerous Denizens - The Monsters of Tellene|4
  Improved grab|10|Large|18|Dinosaur, Cryptoclidus|Monster Manual II|3 has no land speed
  Improved grab|16|Large|27|Bear, Brown|Monster Manual|6
  Improved grab|18|Large|27|Bear, Polar|Monster Manual|8
  Improved grab|23|Large|31|Bear, Dire|Monster Manual|12

Of course, an animal could in theory be trained to grapple even if it doesn't naturally do so. This isn't terribly important, but can fill in a few gaps.

.. code-block:: bash

  sqlite> select distinct (hit_dice*3/4 + (strength - 10)/2 + (size_id - 5)*4), dnd_racesize.name, strength, dnd_monster.name, dnd_rulebook.name, hit_dice from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where dnd_monstertype.name="Animal" order by (hit_dice*3/4 + strength/2 + size_id*4), -hit_dice;
  2|Medium|14|Phynxkin|Dragon Magic|1
  11|Large|18|Horse, Warhorse, Heavy|Monster Manual|4
  12|Large|21|Ape|Monster Manual|4
  13|Large|23|Drakkensteed|Dragon Magic|4
  19|Medium|30|Ape, Legendary|Monster Manual II|13
  55|Colossal|40|Dinosaur, Seismosaurus|Monster Manual II|32

Bigger animals are better at tripping...it helps to think of it not in terms of the word trip, but in terms of knocking someone prone.

.. code-block:: bash

  sqlite> select distinct dnd_special_ability.name, ( (strength - 10)/2 + (size_id - 5)*4), dnd_monstertype.name, dnd_racesize.name, strength, dnd_monster.name, dnd_rulebook.name, hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstertype.name="Animal" or (dnd_monstertype.name="Magical Beast" and intelligence<3) ) and dnd_special_ability.name like "%trip%" order by (strength/2 + size_id*4), -DC, -size_id;
  Trip|2|Medium|15|Bat, Hunting|Monster Manual II|4
  Trip|2|Medium|14|Hyena|Monster Manual|2
  Trip|3|Medium|16|Cheetah|Monster Manual|3
  Trip|3|Medium|17|War Mastiff|Heroes of Battle|3
  Trip|7|Medium|25|Wolf, Legendary|Monster Manual II|14
  Trip|9|Large|20|Jackal, Dire|Sandstorm|4
  Trip|11|Large|25|Wolf, Dire|Monster Manual|6
  Knockback|Brixashulty|Races of the Wild|2
  Knockback (Ex): A gore attack from a brixashulty can literally drive back a foe. When a brixa hits with its gore attack, it can immediately attempt a bull rush without entering the foe's space or provoking an attack of opportunity. The brixa makes a Strength check with a +7 bonus, which includes a +4 racial bonus. If the bull rush succeeds, the foe is driven back 5 feet and must make a DC 12 Reflex save or fall down. If being driven back would force the opponent into a barrier or into a square where it cannot stop (such as a wall or a square that already contains another creature), the foe falls down in its square instead.
  A brixashulty kid is worth 30 gp and is ready for training by age two. It can live for up to 50 years.

  sqlite> select distinct ( (strength - 10)/2 + (size_id - 5)*4), dnd_monstertype.name, dnd_racesize.name, strength, dnd_monster.name, dnd_rulebook.name, hit_dice from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where dnd_monstertype.name="Animal" and land_speed is not null order by (strength/2 + size_id*4), -hit_dice;
  4|Medium|19|Bear, Black|Monster Manual|3
  4|Medium|19|Crocodile|Monster Manual|3
  8|Large|18|Camel|Monster Manual|3
  10|Large|22|Ape, Dire|Monster Manual|5
  10|Large|22|Bison|Monster Manual|5
  10|Large|23|Drakkensteed|Dragon Magic|4
  11|Large|25|Lizard, Giant, Footpad|Drow of the Underdark|5
  12|Large|27|Bear, Brown|Monster Manual|6
  16|Huge|27|Crocodile, Giant|Monster Manual|7

Unfortunately, without a source of data on feats, we cannot know which animals have the Track feat. On the other hand, Handle Animal might make the Track feat irrelevant: Track (DC 20): The animal tracks the scent presented to it. (This requires the animal to have the scent ability.)

.. code-block:: bash

  sqlite> select distinct dnd_special_ability.name, (wisdom - 10)/2, dnd_monstertype.name, dnd_racesize.name, dnd_monster.name, dnd_rulebook.name, hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstertype.name="Animal" or (dnd_monstertype.name="Magical Beast" and intelligence<3) ) and dnd_special_ability.name like "%scent%" order by wisdom/2, -DC;
  scent|1|Small|Dog|Monster Manual|1 has Track feat Dogs have a +4 racial bonus on Survival checks when tracking by scent.
  scent|1|Fine|Mouse|Dungeon Master's Guide v.3.5|-4 no Track feat
  scent|2|Small|Vulture|Sandstorm|1 has Track feat A vulture has a +4 racial bonus on Spot and Survival checks.
  scent|3|Medium|Bat, Hunting|Monster Manual II|4 ironically does not have the Track feat
  scent|3|Small|Dinosaur, Swindlespitter|Monster Manual III|2 no Track feat

Just for fun, remember that Moonrats are indistinguishable from normal rats except in moonlight. If someone did use a rat as a tracker underground, it might turn out that Handle Animal stops working when it gets under the open sky...

.. code-block:: bash

  sqlite> select distinct dnd_special_ability.name, (wisdom - 10)/2, dnd_monstertype.name, dnd_racesize.name, land_speed, dnd_monster.name, dnd_rulebook.name, hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstertype.name="Animal" or (dnd_monstertype.name="Magical Beast" and intelligence<3) ) and (dnd_special_ability.name like "%sense%" or dnd_special_ability.name like "%sight%") order by dnd_special_ability.name, wisdom/2, -DC;
  Blindsight 100ft|2|Huge|20|Sea Tiger|Monster Manual III|10
  Blindsight 60ft|2|Medium|40|Nifern|Serpent Kingdoms|2
  Blindsense 120ft|3|Medium|20|Bat, Hunting|Monster Manual II|4
  Blindsense 60ft|2|Tiny|10|Chordevoc|Races of the Wild|1
  Blindsense 40ft|2|Large|20|Bat, Dire|Monster Manual|4
  Blindsense 20ft|2|Diminutive|5|Bat|Monster Manual|-4
  Blindsight 1200ft|5|Magical Beast|Gargantuan|50|Malastor|Monster Manual V|25
  Blindsight 120ft|2|Magical Beast|Small|10|Bakkas|Garden of the Plantmaster|6
  Blindsight 90ft|0|Magical Beast|Small|20|Darkmantle|Monster Manual|6
  tremorsense 1200ft|5|Magical Beast|Gargantuan|50|Malastor|Monster Manual V|25
  tremorsense 60ft|1|Magical Beast|Medium|20|Thrum Worm|Races of Stone|7
  tremorsense 60ft|1|Magical Beast|Large|30|Ankheg|Monster Manual|8

`Chordevoc <http://archive.wizards.com/default.asp?x=dnd/ex/20050204a&page=5>`_

.. code-block:: bash

  sqlite> select distinct dnd_special_ability.name, 10 + hit_dice/2 + (constitution - 10)/2 as virulence, dnd_monstertype.name, dnd_racesize.name, land_speed, dnd_monster.name, dnd_rulebook.name, hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstertype.name="Animal" or (dnd_monstertype.name="Magical Beast" and intelligence<3) ) and (dnd_special_ability.name like "%poison%" or dnd_special_ability.name like "%venom%" or dnd_special_ability.name like "%drain%") and dnd_special_ability.name!="immunity to poison" and dnd_special_ability.name!="resistance to poison" order by virulence, -DC;
  poison|8|Diminutive|15|Hedgehog|Dungeon Master's Guide v.3.5|-4 Dexterity
  Poison|8|Tiny|10|Sea Snake, Tiny|Stormwrack|-4
  Poison|10|Small|10|Sea Snake, Small|Stormwrack|1 Constitution Poison (Ex): A sea snake's poison is extraordinarily virulent. It has a +2 racial bonus on the poison's save DC.
  Poison|10|Small||Stingray|Stormwrack|1 Poison (Ex): Injury, Fortitude DC 12, nauseated 1d4 hours/1d3 Dex. The save DC is Constitution-based and includes a +2 racial bonus. A creature that makes its saving throw against the poison's initial damage is instead sickened for 1d6 rounds. Blood Web (Ex) A bloodsilk spider can throw a blood-red web eight times per day. An entangled creature can escape with a DC 11 Escape Artist check or burst the web with a DC 15 Strength check. Both are standard actions.
  poison|10|Small|20|Dragon Newt|Web|1 Strength http://archive.wizards.com/default.asp?x=dnd/mm/20030920a
  Poison spray|12|Small|30|Dinosaur, Swindlespitter|Monster Manual III|2 Poison Spray (Ex): When threatened, a swindlespitter sprays a corrosive poison in a 15-foot cone from its mouth. Contact; Fort DC 12; initial damage blindness for 2d4 minutes; secondary damage 1d4 Con. The swindlespitter can spray this poison once every 1d4 rounds. Swindlespitters flee from blinded opponents if possible.
  Venom spray|13|Medium|20|Sailsnake|Monster Manual IV|3 Venom Spray (Ex) 20-ft. cone, once every 6 rounds, blind for 1d4 rounds, Fortitude DC 13 half.
  Poison|13|Medium|40|Nifern|Serpent Kingdoms|2 paralysis then Strength
  blood drain|11|Medium|40|Weasel, Dire|Monster Manual|3 Blood Drain (Ex): A dire weasel drains blood for 1d4 points of Constitution damage each round it remains attached.
  poison|14|Medium|30|Toad, Dire|Monster Manual II|4 Constitution
  poison|14|Medium|50|Dinosaur, Fleshraker|Monster Manual III|4 Dexterity
  poison|16|Huge|30|Snake, Dire|Monster Manual II|7 Constitution
  poison|21|Huge|20|Lizard, Giant Banded|Sandstorm|10 Strength
  poison|25|Large|30|Snake, Legendary|Monster Manual II|16 Constitution

  poison|17|Magical Beast|Large|30|Spider Eater|Monster Manual|9 Poison (Ex): Injury, Fortitude DC 17, initial damage none, secondary damage paralysis for 1d8+5 weeks. The save DC is Constitution-based.
  Mlarraun Poison (Ex): spit, contact, Fortitude DC11, initial damage blindness 2d6hours, secondary damage blindness 4d6hours and 1d4 points of damage. The poison need not touch the eyes to cause blindness.


.. code-block:: bash

  sqlite> select distinct dnd_monstertype.name, dnd_racesize.name, fine_biped_max_load_ounces*quadruped_carry_factor/3/16, land_speed, dnd_monster.name, dnd_rulebook.name, hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id natural join carrying_capacity inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where dnd_monstertype.name="Animal" or (dnd_monstertype.name="Magical Beast" and intelligence<3) order by land_speed, fine_biped_max_load_ounces*quadruped_carry_factor/3/16, -DC;
  Colossal|51200|20|Dinosaur, Seismosaurus|Monster Manual II|32
  Colossal|89600|20|Dinosaur, Diplodocus|Dragon Magazine|28
  Gargantuan|25600|30|Elephant, Dire|Monster Manual II|20
  Medium|87|40|Phynxkin|Dragon Magic|1
  Medium|100|40|Dog, Riding|Monster Manual|2
  Medium|100|40|Pony, War|Monster Manual|2
  Medium|115|40|Nifern|Serpent Kingdoms|2
  Medium|130|40|War Mastiff|Heroes of Battle|3
  Medium|130|40|Pony, Whiteshield|Champions of Valor|2
  Medium|175|40|Bear, Black|Monster Manual|3
  Large|350|40|Titan Salamander|Web|4
  Gargantuan|19200|40|Dinosaur, Giganotosaurus|Dragon Magazine|24
  Medium|87|50|Hyena|Monster Manual|2
  Medium|115|50|Cheetah|Monster Manual|3
  Large|300|50|Horse, Warhorse, Heavy|Monster Manual|4
  Large|18|50|Camel|Monster Manual|3
  Large|18|50|Horse, Draft|Dangerous Denizens - The Monsters of Tellene|3
  Large|23|50|Drakkensteed|Dragon Magic|4
  Large|25|50|Wolf, Dire|Monster Manual|6
  Huge|39|50|Bear, Polar, Dire|Frostburn|18
  Medium|11|60|Deer|Silver Marches|2
  Medium||60|Dinosaur, Deinonychus|Monster Manual|4 biped
  Large|16|60|Horse, Warhorse, Light|Monster Manual|3
  Large|20|60|Jackal, Dire|Sandstorm|4
  Large|21|60|Dinosaur, Megaraptor|Monster Manual|8 biped
  Large|22|60|Horse, Dire|Monster Manual II|8
  Large|15|65|Axebeak|Arms & Equipment Guide|3 Axebeaks move five times their normal speed when running instead of four times the speed. Axebeak eggs are worth 20 gp on the open market. Note that axebeaks are bipeds, so cannot carry as much as the formula would indicate.
  Large|29|80|Horse, Legendary|Monster Manual II|18

  sqlite> select distinct dnd_racesize.name, fine_biped_max_load_ounces*quadruped_carry_factor/3/16, abbrev, speed, dnd_monster.name, dnd_rulebook.name, hit_dice from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join monster_movement_mode on dnd_monster.id=monster_id inner join dnd_racesize on size_id=dnd_racesize.id natural join carrying_capacity inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where dnd_monstertype.name="Animal" order by abbrev, speed, fine_biped_max_load_ounces*quadruped_carry_factor/3/16, -hit_dice;
  Tiny|17|b|5|Lizard, Horned|Sandstorm|1
  Medium|87|b|10|Wolverine|Monster Manual|3
  Large|520|b|20|Dinosaur, Bloodstriker|Monster Manual III|9
  Huge|1840|b|20|Tortoise, Dire|Sandstorm|14
  Medium|87|c|10|Wolverine|Monster Manual|3
  Large|520|c|10|Wolverine, Dire|Monster Manual|5
  Huge|2400|c|10|Lizard, Giant Banded|Sandstorm|10
  Medium|87|c|20|Phynxkin|Dragon Magic|1
  Medium|100|c|30|Baboon|Monster Manual|1 should be treated as quadruped when climbing
  Large|460|c|30|Ape|Monster Manual|4 should be treated as quadruped when climbing
  Large|800|c|30|Lizard, Giant, Footpad|Drow of the Underdark|5
  Large|350|c|40|Lizard, Giant, Quicksilver|Drow of the Underdark|4
  Medium|75|c|60|Dinosaur, Cliff Raptor|Web|4 Climb +17 http://archive.wizards.com/default.asp?x=dnd/fw/20040509a
  Large|800|c|60|Forest Sloth|Monster Manual II|14 Climb +15
  Large|260|f|40|Bat, Dire|Monster Manual|4
  Huge|1600|f|40|Bat, War|Monster Manual II|10
  Medium|100|f|60|Bat, Hunting|Monster Manual II|4
  Large|600|f|60|Drakkensteed|Dragon Magic|4
  Large|300|f|80|Dinosaur, Pteranadon|Serpent Kingdoms|3
  Gargantuan|11200|f|80|Roc|Monster Manual|18
  Huge|1840|f|100|Dinosaur, Quetzelcoatlus|Monster Manual II|10

Bats have good maneuverability.

Unfortunately the database does not yet include skill ranks, so we cannot sort by the kinds of walls an animal can climb.

Baboons can carry up to a hundred pounds, three hundred pounds if they accept moving slower.
Baboons have a +10 Climb modifier and can always take 10, so it can climb An uneven surface with some narrow handholds and footholds, such as a typical wall in a dungeon or ruins, but cannot climb a DC25 wall such as a natural rock wall or a brick wall.
Baboon Rock in Tanzania, Africa https://www.youtube.com/watch?v=42Px9N7jV7w&t=33s

Burrowing is of questionable usefulness. A creature with a burrow speed can tunnel through dirt, but not through rock unless the descriptive text says otherwise. Most burrowing creatures do not leave behind tunnels other creatures can use.

40gp 25pound Saddle, Burrower's: This specialized exotic saddle allows the rider to stay safely on a mount that has the ability to burrow. The saddle includes a secure system of straps and buckles that holds the rider fl ush to the burrowing mount's back. In addition, a thick, round-edged piece of leather reinforced with bone or wood rises from the front of the shield, just before the rider's seat, roughly to the height of the rider's chest. The curved piece of leather bends up and toward the rider, allowing her to duck behind it while her mount burrows, shielding her from most of the dirt and rocks that might otherwise tear the rider from her perch, straps or no straps. Similar bits of reinforced leather protect the front and sides of the rider's legs.
 Strapping oneself to the saddle requires three consecutive full-round actions that provoke attacks of opportunity. Unbuckling the straps is a full-round action that provokes attacks of opportunity. While strapped into the saddle, you lose your Dexterity bonus to Armor Class and take a -4 penalty on all attack rolls.
 Weight given is for a saddle meant for a Large creature. Saddles made for Medium mounts weigh half this amount, and saddles made for Huge creatures weigh twice as much.

A burrowing ankheg usually does not make a usable tunnel, but can construct a tunnel; it burrows at half speed when it does so.


Technically, Handle Animal can work on any creature with an Intelligence score of 1 or 2 (which are also vulnerable to Ray of Stupidity), which technically includes any creature that has been Feebleminded, but making a creature friendly enough to be willing to be trained is a sticking point.
A druid can also use Wild Empathy to influence a magical beast with an Intelligence score of 1 or 2, but she takes a -4 penalty on the check. Wild animals are usually unfriendly, so it takes a DC15 check to make it indifferent, DC25 to make it friendly.
Trainable (Ex): A thrum worm is easier to train and handle than most other magical beasts. Handle Animal checks made to train or handle a thrum worm are not increased by 5. Gnomes receive a +2 circumstance bonus on all Handle Animal checks made to train or handle a thrum worm.

.. code-block:: bash

  sqlite> select distinct dnd_racesize.name, fine_biped_max_load_ounces*quadruped_carry_factor/3/16, abbrev, speed, dnd_monster.name, dnd_rulebook.name, hit_dice from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join monster_movement_mode on dnd_monster.id=monster_id inner join dnd_racesize on size_id=dnd_racesize.id natural join carrying_capacity inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where dnd_monstertype.name="Magical Beast" and intelligence<3 and abbrev='c' order by fine_biped_max_load_ounces*quadruped_carry_factor/3/16, -hit_dice, speed;
  No magical beasts make significantly better climbers than the best animals.




On a lighter note, I always thought that a "living will" sounded like a magical incorporeal construct. Say, are there any incorporeal constructs?

.. code-block:: bash

  sqlite> select distinct dnd_monster.name,challenge_rating from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join monster_subtype on dnd_monster.id=monster_subtype.monster_id inner join dnd_monstersubtype on monster_subtype.subtype_id=dnd_monstersubtype.id where (dnd_monstertype.name="Construct") and (dnd_monstersubtype.name="Incorporeal") order by challenge_rating;
  Umbral Spy|3
  Golem, Prismatic|18




