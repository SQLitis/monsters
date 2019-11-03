
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

  sqlite> select dnd_monster.name, dnd_rulebook.name from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_rulebook on rulebook_id=dnd_rulebook.id where dnd_monstertype.name="Humanoid" and not exists (select 1 from monster_has_special_ability inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id and monster_has_special_ability.monster_id=dnd_monster.id and (dnd_special_ability.name like "%darkvision%" or dnd_special_ability.name like "%low-light vision%") );
  Lizardfolk|Monster Manual v.3.5
  Locathah|Monster Manual v.3.5
  Changeling|Monster Manual III
  Maenad|Expanded Psionics Handbook
  Mongrelfolk|Fiend Folio
  Selkie (humanoid form)|Fiend Folio
  Skulk|Fiend Folio
  Neanderthal|Frostburn
  Azurin|Magic of Incarnum
  Rilkan|Magic of Incarnum
  Skarn|Magic of Incarnum
  Asherati|Sandstorm
  Bhuka|Sandstorm
  Aventi|Stormwrack
  Darfellan|Stormwrack
  Hadozee|Stormwrack
  Karsite|Tome of Magic
  Phaerlock|Underdark
  Dabus|Expedition to the Demonweb Pits
  Hai Nu|Oriental Adventures


In 3.5, skeletons and zombies were changed to be evil. Are there still any non-evil undead in 3.5?
We don't have edition data in the rulebook table yet, but a spot-check reveals there definitely is one:

.. code-block:: bash

  sqlite> select distinct dnd_monster.name, intelligence, law_chaos, dnd_monstertype.name, dnd_rulebook.name from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on dnd_racesize.id=size_id inner join monster_has_alignment on dnd_monster.id=monster_has_alignment.monster_id inner join dnd_rulebook on dnd_monster.rulebook_id=dnd_rulebook.id where dnd_monstertype.name="Undead" and good_evil!=-1 order by intelligence is null, challenge_rating;
  Haunt, Taunting|13|C|Undead|Monster Manual V



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

  sqlite> select distinct challenge_rating, dnd_monster.name, dnd_monstertype.name || " (" || group_concat(distinct dnd_monstersubtype.name) || ")", max(CASE subtype2.name WHEN "Extraplanar" THEN "Extraplanar" ELSE NULL END), dnd_rulebook.name from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join monster_has_subtype on dnd_monster.id=monster_has_subtype.monster_id inner join dnd_monstersubtype on monster_has_subtype.subtype_id=dnd_monstersubtype.id LEFT JOIN monster_has_subtype AS hasSubtype2 ON hasSubtype2.monster_id=dnd_monster.id LEFT JOIN dnd_monstersubtype AS subtype2 ON subtype2.id=hasSubtype2.subtype_id inner join dnd_rulebook on rulebook_id=dnd_rulebook.id where (dnd_monstertype.name="Outsider" or dnd_monstertype.name="Elemental" or (subtype2.name="Extraplanar") ) and (dnd_monstersubtype.name="Water" or dnd_monstersubtype.name="Aquatic") GROUP BY dnd_monster.id ORDER BY challenge_rating;
  -2|Gen, Water|Outsider (Aquatic,Water)|Extraplanar|Dragon Magazine
    Elemental Travel (Sp): A gen can plane shift at will to any of the Elemental Planes or from any elemental plane to the Material Plane. This ability transports the gen only. It is otherwise identical to the plane shift spell (caster level 13th).
  2|Elemental Grue, Vardigg|Water|Elemental|Complete Arcane
    Water Jet (Sp): As a standard action, a water grue can create a tremendously powerful 30-foot line of water. Any creature in the area of the line takes 2d6 points of damage (Reflex DC 11 negates). A creature failing the saving throw must succeed on a Strength check or a Balance check (DC 5 + damage dealt) or be knocked prone by the force of the blast.
  3|Mephit, Water|Water|Outsider|Monster Manual v.3.5
  Tojanida, Juvenile|3
  4|Demon, Skulvyn|Aquatic|Outsider|Fiend Folio
    Wounding (Ex): Wounds resulting from a skulvyn's tail lash attacks bleed for an additional 1 point of damage per round thereafter. Multiple wounds from such attacks result in cumulative bleeding loss
    Slow Aura (Su): Living creatures that come within 30 feet of a skulvyn must make a Will save (DC 12) or become slowed for 4 rounds.
  4|Demon, Elemental, Water|Water|Outsider|Dragon Compendium
    Waters of Fire (Su): A swimming water demon can open the vents along its torso and forcefully expel gouts of superheated steam that cause the water in a 30-foot radius to boil.
  4|Nereid|Fey (Aquatic)|Extraplanar|Stormwrack
    Drown (Su): A nereid can make a special touch attack to try to fill an opponent's lungs with water.
  Tojanida, Adult|5
  5|Orlythys|Water|Outsider|Dragon Magazine
  5|Elemental Weird, Water, Lesser|Water|Elemental|Dragon Magazine
  8|Yugoloth, Echinoloth|Aquatic|Outsider|Stormwrack
    Infernal Wound (Su): The damage an echinoloth deals as it rends with its terrible hooked tentacles causes persistent wounds. Any creature injured by the echinoloth's rend attack loses 1 additional hit point each round.
  Tojanida, Elder|9
  9|Aspect of Dagon|Aquatic|Outsider|Fiendish Codex I
    Form of Madness (Su) Anyone within 60 feet of an aspect of Dagon must make a Will save (DC 17). Failure indicates the creature develops an overwhelming fear of the ocean and its depths.
  9|Genie, Marid|Water|Outsider|Manual of the Planes
    Spell-Like Abilities: At will create water, detect evil, detect good, detect magic, invisibility, purify food and drink (water only), see invisibility; 5/day control water, gaseous form, solid fog, water breathing; 1/year limited wish (to nongenies only).
  9|Caller from the Deeps|Water|Elemental|Stormwrack
    Summon Watery Ally (Sp): Once per hour, a caller from the deeps can summon a Medium water elemental or a Large fiendish shark. This creature remains for 10 minutes or until slain.
  12|Elemental Weird, Water|Water|Elemental|Monster Manual II
     A water weird can cast arcane spells and divine spells from the Water and Healing domains as an 18th-level sorcerer.
  13|Aspect of Sekolah|Aquatic|Outsider|Fiendish Codex II
  13|Scyllan|Aquatic|Outsider|Stormwrack
     Control Water (Sp): 1/hour, caster level 16th.
  15|Avatar of Elemental Evil, Waterveiled Assassin|Water|Elemental|Monster Manual IV
  17|Elemental, Water, Monolith|Water|Elemental|Complete Arcane
  17|Demon, Wastrilith|Aquatic|Outsider|Fiend Folio
     Breath Weapon (Su): Cone of boiling water, 3d10 points of damage, 60 feet, every 1d4 rounds; Reflex DC 21 half.
     Break Summoning (Ex): If summoned via a summon monster spell, a wastrilith can make an opposed Wisdom check to break free of the summoning. If it succeeds, it then goes on a rampage, attacking the summoner.
     Spell-Like Abilities: At will blasphemy, control water
     Three times per day, a wastrilith can cast summon monster IX as a 17th-level wizard. It can only summon aquatic and water-based creatures, such as fiendish sharks or squids and water elementals. Wastriliths can be summoned using a summon monster IX spell.
      Immunity to Water (Ex): Wastriliths are immune to attacks that are based on water.
  21|Demon, Myrmyxicus|Aquatic|Outsider|Fiend Folio
     3/day control water, control weather
  22|Dagon (Prince of the Depths)|Aquatic|Outsider|Fiendish Codex I
  22|Olhydra (Princess of Evil Water Creatures, Princess of Watery Evil, Mistress of the Black Tide)|Water|Elemental|Dragon Magazine
  22|Ben-hadar (Prince of Good Water Creatures, Squallbringer, The Valorous Tempest)|Water|Elemental|Dragon Magazine

Here we can see that a water gen is listed as CR -2...huh?
To avoid dealing with floating-point numbers at all other times, fractions of the form 1/x are stored as negative integers.
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




Miscellaneous trainable creature abilities:

.. code-block:: bash

  sqlite> select distinct dnd_special_ability.name, dnd_monster.name, dnd_rulebook.name, hit_dice from dnd_monster inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id left join monster_has_subtype on dnd_monster.id=monster_has_subtype.monster_id left join dnd_monstersubtype on subtype_id=dnd_monstersubtype.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where dnd_monstertype.name="Animal" and (dnd_monstersubtype.name is null or dnd_monstersubtype.name!="Swarm") and dnd_special_ability.name not like "%resistan%" and dnd_special_ability.name not like "%saves vs. spells%" and dnd_special_ability.name not like "immun%" and dnd_special_ability.name not like "disease%" and dnd_special_ability.name not like "%powerful%" and dnd_special_ability.name not like "double damage %" and dnd_special_ability.name!="Augmented critical" and dnd_special_ability.name!="Evasion" and dnd_special_ability.name!="uncanny dodge" and dnd_special_ability.name not like "%trample%" and dnd_special_ability.name!="stampede" and dnd_special_ability.name not like "rake %" and dnd_special_ability.name not like "rend 2d%" and dnd_special_ability.name not like "constrict %" and dnd_special_ability.name not like "swallow whole" and dnd_special_ability.name not like "coil slam 1d%" and dnd_special_ability.name not like "%tail sweep%" and dnd_special_ability.name not like "%Frenzy" and dnd_special_ability.name not like "rage" and dnd_special_ability.name != "Ferocity" and dnd_special_ability.name!="Damage Reduction" and dnd_special_ability.name!="Low-Light Vision" and dnd_special_ability.name!="Darkvision" and dnd_special_ability.name!="light sensitivity" and dnd_special_ability.name not like "%scent" and dnd_special_ability.name not like "improved grab"and dnd_special_ability.name not like "trip" and dnd_special_ability.name not like "pounce" and dnd_special_ability.name not like "blinds%" and dnd_special_ability.name not like "tremorsense %" and dnd_special_ability.name not like "hold breath" and dnd_special_ability.name not like "poison%" and dnd_special_ability.name not like "venom%" and dnd_special_ability.name!="blood drain" order by hit_dice;
  sprint|Cheetah|Monster Manual|3
  Fast Healing|Snake, Glacier|Serpent Kingdoms|2
  Wounding|Bat, Guard|Monster Manual II|4
  Acid spit|Dragon Newt|Web|1 Spit (Ex): The dragon newt can spit acidic globules with a range increment of 10 feet. This is a ranged touch attack that deals 1d4 points of acid damage.
  Acidic bite|Titan Salamander|Web|4 Acidic Bite (Ex): The titan salamander's saliva is caustic and inflicts 1d6 points of additional acid damage on a successful bite attack. http://archive.wizards.com/default.asp?x=dnd/mm/20030920a
  Blood squirt|Dinosaur, Bloodstriker|Monster Manual III|9 Blood Squirt (Ex): Every 1d4 rounds, a bloodstriker can
project a 30-foot line of its acidic blood as a standard action. Anyone in the area takes 2d6 points of acid damage (Reflex DC 19 half).

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
  PLAs|Chekryan|Sandstorm|8 Dimension Door 1/day can take along one Medium creature
  silence|Rothé, Ghost|Forgotten Realms Campaign Setting|9
  Breath weapon 3d6 fire every 1d4 rounds|Horned Beast|Tome of Magic|9
  Growth|Blood Ape|Monster Manual II|9 the ability to return to Large size means that blood apes require substantially less food than Huge creatures would.
  Petrification|Cockatrice|Monster Manual|10
  Petrifying gaze|Basilisk|Monster Manual|11
  Controlling sting|Quanlos|Monster Manual IV|11
  Reverse gravity|Gravorg|Monster Manual II|15
  Plane shift|Gaspar|Planar Handbook|19
  Trill|Frost Worm|Monster Manual|19
  Breath weapon (petrification)|Magical Beast|Gorgon|Monster Manual v.3.5|28
  Acid spray|Magical Beast|Digester|Monster Manual v.3.5|28
  Null psionic exhalation|Magical Beast|Gray Glutton|Expanded Psionics Handbook|29
  ice step|Magical Beast|Spawn of Tiamat, Whitespawn Iceskidder|Monster Manual IV|29
   Ice Step (Ex) Whitespawn iceskidders ignore all movement penalties associated with snow or ice on the ground.
  armor damage|Magical Beast|Rampager|Monster Manual II|34
  vorpal tusks|Magical Beast|Razor Boar|Monster Manual II|35
  Avalanche wave|Magical Beast|Malastor|Monster Manual V|40

Controlling Sting (Su) As the dominate monster spell; 3/day; Fort DC 19 negates; caster level 10th.
A quanlos's puny intellect prevents it from exercising a fine level of control over its thralls. The creature lacks the sophistication to order a group of dwarf artisans to build a castle for it, or to command an elf wizard to use a specific spell to protect it. Instead, it relies on a limited set of general commands: attack, defend, gather food, and so forth.
A quanlos can control a number of creatures equal to its total Hit Dice at one time. If it takes control of a creature beyond this limit, it must choose one of its thralls to release from service.

Reverse Gravity (Sp): At will, a gravorg can produce an effect like that of a reverse gravity spell (caster level 10th; Reflex save DC 18), except that the range is 200 feet and it affects an area of up to five 10-foot cubes.

Technically, you can use Handle Animal on *any* creature with an intelligence of 1 or 2.

.. code-block:: bash

  sqlite> select distinct dnd_special_ability.name, dnd_monstertype.name, dnd_monster.name, dnd_rulebook.name, 15 + max(0,hit_dice) + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id left join monster_has_subtype on dnd_monster.id=monster_has_subtype.monster_id left join dnd_monstersubtype on subtype_id=dnd_monstersubtype.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (intelligence=1 or intelligence=2) and (dnd_monstersubtype.name is null or dnd_monstersubtype.name!="Swarm") and dnd_special_ability.name not like "%resistan%" and dnd_special_ability.name not like "%saves vs. spells%" and dnd_special_ability.name not like "immun%" and dnd_special_ability.name not like "disease%" and dnd_special_ability.name not like "%powerful%" and dnd_special_ability.name not like "double damage %" and dnd_special_ability.name!="Augmented critical" and dnd_special_ability.name!="Evasion" and dnd_special_ability.name!="uncanny dodge" and dnd_special_ability.name not like "%trample%" and dnd_special_ability.name!="stampede" and dnd_special_ability.name not like "rake %" and dnd_special_ability.name not like "rend 2d%" and dnd_special_ability.name not like "constrict %" and dnd_special_ability.name not like "swallow whole" and dnd_special_ability.name not like "coil slam 1d%" and dnd_special_ability.name not like "%tail sweep%" and dnd_special_ability.name not like "%Frenzy" and dnd_special_ability.name not like "rage" and dnd_special_ability.name != "Ferocity" and dnd_special_ability.name!="Damage Reduction" and dnd_special_ability.name!="Low-Light Vision" and dnd_special_ability.name!="Darkvision" and dnd_special_ability.name!="light sensitivity" and dnd_special_ability.name not like "%scent" and dnd_special_ability.name not like "improved grab"and dnd_special_ability.name not like "trip" and dnd_special_ability.name not like "pounce" and dnd_special_ability.name not like "blinds%" and dnd_special_ability.name not like "tremorsense %" and dnd_special_ability.name not like "hold breath" and dnd_special_ability.name not like "poison%" and dnd_special_ability.name not like "venom%" and dnd_special_ability.name!="blood drain" and dnd_special_ability.name not like "Amphibious" and dnd_special_ability.name not like "Stench" and dnd_special_ability.name not like "Attach" and dnd_monster.name not like "%hydra, %" and DC<=25 order by -DC;
  planar rip|Outsider|Ether Scarab|Monster Manual II|21
  Greater invisibility|Plant|Phantom Fungus|Monster Manual v.3.5|22
  Paralysis|Aberration|Carrion Crawler|Monster Manual v.3.5|23 Paralysis (Ex): Those hit by a carrion crawler's tentacle attack must succeed on a DC 13 Fortitude save or be paralyzed for 2d4 rounds. The save DC is Constitution-based. Full Attack: 8 tentacles +3 melee (paralysis). So while the DC and duration is unimpressive compared to a nifern or spider-eater, carrion crawlers sure do get a lot of chances.
  walk corpse|Aberration|Gutpuppet|Web|24 http://archive.wizards.com/default.asp?x=dnd/mm/20011215a
  charging form|Undead|Bonespur|Monster Manual V|24
  Rust|Aberration|Rust Monster|Monster Manual v.3.5|25
  Burn|Elemental|Elementite Swarm, Fire|Planar Handbook|27
  earth glide|Elemental|Elementite Swarm, Earth|Planar Handbook|27
  Fear aura|Monstrous Humanoid|Buso, Tigbanua|Oriental Adventures|28
  pass without trace|Undead|Skeletal Warbeast|Heroes of Battle|28
  wing slash|Aberration|Slasrath|Fiend Folio|28  If a slasrath charges, it can end the charge with a wing slash attack. The slasrath makes a +9 melee attack against each creature it threatens at the end of its charge. Each creature hit takes 3d6+10 points of damage. [Presumably it can take a -4 penalty to deal nonlethal damage, as normal.] Additionally, if an armor wearing creature takes damage from this attack, the creature must make a Reflex saving throw (DC 19) or the armor is shredded away instantly.
  SLAs|Plant|Twilight Guardian|Dragon Magic|28
   at-will Transport Via Plants carries along two Medium-size willing creatures (or one Large) and gear an unlimited distance.
  hive mind|Outsider|Demonhive Queen|Monster Manual IV|28
  confusion|Construct|Rogue Eidolon|Monster Manual II|29
  Magnetic attraction|Aberration|Lodestone Marauder|Monster Manual IV|31
  Possess object|Undead|Golem Remnant|Web|36 http://archive.wizards.com/default.asp?x=dnd/fw/20041126a
  Disintegration|Aberration|Annihilator|Underdark|40

Animals can be trained for a very specific function, like old-timey turnspit dogs.

Upon encountering a humanoid or animal corpse, the Gutpuppet crawls into the lifeless chest through the victim's mouth and extends tendrils to deliver its horrible ichor. It takes over the victim's circulatory system and floods the body with its own fluids. This process happens quickly, usually taking no more than three or four minutes. The gutpuppet flushes out the corpse's fluids to make room for its own. This is a particularly violent and gory process: Witnesses report seeing the heaving chest of a dead body, a wet, ragged breathing-like sound coming from the mouth, then a sudden gout of blood bursting from every opening of the body accompanied by a violent, grotesque, lifelike twitching.
However, the gutpuppet is keen to pick bodies that are intact. Any gross openings in the skin will allow too much of its fluid to leak out. Therefore, a gutpuppet is more likely to pick a body that has died from blunt trauma than from, say, being hacked to death. It prefers animals and people that have died from sickness. If it cannot find a corpse, it chooses some place to wait until it smells a corpse. (It can smell a dead body from up to a mile away.) It prefers moist hiding places; ideal locations include coastal caves, since they're dark and wet, and stagnant lakes.
Once the gutpuppet is firmly attached inside the body, has flushed all the body's blood and other fluids out, and filled it with its own, it's ready to "walk the corpse." On its own, the gutpuppet is very slow, but it can walk a corpse easily -- sometimes moving faster than the original owner could.
When a gutpuppet traveling inside a corpse encounters another dead body (nearly anything will do), it "spits" one of its spikes into the body. The spike injects fluid into the corpse, and the spike itself slowly burrows into the body, toward the heart, then grows. Within two days, a new gutpuppet fills the chest of the corpse, animates the body, and walks around searching for dead bodies on its own.
To aid the appearance of being just an ordinary living creature, the gutpuppet washes itself in streams and steals fresh clothing when possible.
Although it is no more intelligent than a particularly bright animal (and certainly cannot speak any language, so using the corpse's money to buy clothing is out of the question), the gutpuppet has a magpie-like attraction to clothing that is, obviously, to its advantage in hiding.
Corpses under the control of a gutpuppet do not resemble zombies or most other undead. First, they do not smell as bad as other forms of undead, as the gutpuppet's fluid prevents flesh and connective tissue from decaying any more than it already has. Third, the corpse's flesh takes on a particularly strange pallor. It's not pale -- certainly not leathery by any means -- but is rather glassy. Such a complexion could be mistaken for a healthy one under the right circumstances, especially on nights with a bright moon. In addition, host bodies profusely sweat the toxin from every pore. This effect, more than anything, can lead someone to mistake a walking corpse for something living. (I, for one, have never encountered another form of undead that can sweat.) Combine this ability with the chest that never stops heaving (as the gutpuppet pushes fluid around the corpse) and the intermittent, ragged, breathing-like sounds coming from the mouth, and one can see how a humanoid corpse might make some distance into civilized areas before being discovered as something not really alive.
A gutpuppet's shell body is easy to track, since every step it takes leaves behind a sweaty footprint. The fluid proves toxic to flesh, but has no effect on other organic material besides making it wet (and remaining toxic to flesh until it evaporates).
Anyone coming into contact with it suffers 1d10 points of temporary Strength damage unless he or she makes a successful Fortitude save (DC 17). Note that a corpse with a gutpuppet inside it also sweats the poison, making contact with the corpse's skin dangerous. Standing fluid is also toxic; anyone touching it suffers 1d10 points of temporary Strength damage unless a successful Fortitude save (DC 17) is made. There is no secondary damage from touching standing gutpuppet fluid.
Gutpuppets do not seek to kill living creatures and try to avoid them. However, they are drawn to blood and, like vultures, seek out living things they sense may die. If attacked, they won't hesitate to defend themselves, spitting spikes at opponents.
The gutpuppet can sustain a corpse for up to a month. While its fluid prevents the decay of muscle and connective tissue, the gutpuppet must eat. The corpse itself is the most convenient source of food, so it nibbles slowly on the inner flesh. Once the body has ceased to be of use, the gutpuppet crawls out through the most accessible opening and inches away, looking for other bodies.

If the carrion crawler isn't horrifying enough for you, and the gutpuppet still isn't horrifying enough for you...
A skull lord's creator skull can create a bonespur from nearby bones and bone shards. Undead created by this ability are automatically under the skull lord's control.
 A skull lord can have a number of undead *under the control* of its creator skull equivalent to an EL 7 encounter. For example, a skull lord might have four bonespurs under its control.
 There is no provision for the creator skull ever losing control of a creature, so this might mean that it cannot create undead in excess of this number.
A spellcaster of 8th level or higher can create a bonespur using the create undead spell. Creating a bonespur requires skeletal remains equivalent to six Medium creatures. (These bonespurs are not automatically under anyone's control.)
Spell-like abilities function like spells, but here we have the special requirement that the creator must be a spellcaster. That can be satisfied by the Fell Conspiracy [Ceremony] feat.
sqlite> select distinct hit_dice, dnd_spell.name, uses_per_day, dnd_monster.name, dnd_monstertype.name, dnd_rulebook.name from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join monster_has_spell_like_ability on monster_has_spell_like_ability.monster_id=dnd_monster.id inner join dnd_spell on monster_has_spell_like_ability.spell_id=dnd_spell.id inner join dnd_rulebook on dnd_monster.rulebook_id=dnd_rulebook.id where dnd_spell.name="Create Undead" order by hit_dice;
9|Create Undead|3|Atropal Scion|Undead|Libris Mortis: The Book of the Dead
10|Create Undead|3|Avolakia|Aberration|Monster Manual II
 Avolakias are experts at infiltrating humanoid societies for a variety of nefarious purposes.
 Although they can digest dead or living flesh, avolakias find both disgusting and resort to such sustenance only under dire circumstances. They prefer to eat undead flesh; fresh off a zombie's flank is best.
 They delight in creating and modifying undead of all sorts, which they use for both food and defense.
 Change Shape (Su): An avolakia can assume the form of any Small or Medium humanoid.
 Spell-Like Abilities: At will chill touch, cause fear, detect magic, disrupt undead, gentle repose, ghoul touch, halt undead, mage hand, read magic, spectral hand; 3/day animate dead, create undead, enervation, vampiric touch. Caster level 14th

Some more powerful creatures can Create Undead at will, but it still takes an hour each, and a pit fiend is unlikely to spend much time on such things.

Alignment: These creatures have animal intelligence, but they are driven by utter loyalty to their creator and the corrupt energy that animates them. They are uniformly lawful evil.
Bonespurs are simple creatures that have little use for trinkets or trophies. However, they sometimes collect wealth from slain opponents as an offering to their masters.
Skull lords probably don't give much thought to what will happen to their bonespurs if the skull lord is destroyed. The most likely place to find a bonespur is near its master's former lair, surrounded by trinkets (some valuable, some valueless, the bonespur can't tell the difference) it has brought as gifts, whining piteously like an abandoned dog, wondering when its master is going to come home.
Realistically, a disturbed bonespur will probably try to chase off anyone nosing around its master's lair, so magical assistance such as Command Undead will probably be necessary before you can begin to train it.

Speed 10 ft. (2 squares), 40 ft. in charging form
Boneshard Blast (Su) Once per day, as a free action immediately following a charge, a bonespur can explode in a shower of bone shards. The shards of the bonespur transform into its normal towering shape at the beginning of its next turn.
Charging Form (Su) Once per day, as a swift action, a bonespur can transform from a column of bone into a rhinolike form. In this form, its speed increases to 40 feet.
When charging, the bonespur transforms into a 12-foot-long rhino-like shape. A bonespur's skeletal form weighs 400 pounds.
When first encountered, a bonespur slashes its bone scythe menacingly before shifting into its charging form and racing at the nearest group of enemies. At the end of its charge, it uses its boneshard blast ability, reshaping into a column of bone on its next turn and attacking all that come within reach.
Though a bonespur is of limited intelligence, it recognizes the advantage of pushing opponents into pits or off ledges, and it makes bull rush attacks whenever possible. At the same time, a bonespur has no sense of self-preservation, and these creatures have been known to follow opponents over the edge of cliffs in the zealousness of a bull rush attack.
Though bonespurs serve at the side of the skull lord or spellcaster who created them, their errands of destruction sometimes see them sent far from their masters.

Large with Strength 18 and a speed of 40feet, bonespurs are decidedly average mounts, except that as undead, they're tireless. They can run forever (at 160feet per round).

.. code-block:: bash

  sqlite> select distinct dnd_monstertype.name, dnd_racesize.name, fine_biped_max_load_ounces*quadruped_carry_factor/3/16, land_speed, dnd_monster.name, dnd_rulebook.name, 15 + hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id natural join carrying_capacity inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where constitution is null and intelligence<3 order by land_speed, fine_biped_max_load_ounces*quadruped_carry_factor/3/16, -DC;
  Undead|Large|300|10|Bonespur|Monster Manual V|24
  Undead|Large|400|50|Skeletal Warbeast|Heroes of Battle|28

.. code-block:: bash

  sqlite> select distinct dnd_racesize.name, fine_biped_max_load_ounces*quadruped_carry_factor/3/16, abbrev, speed, dnd_monster.name, dnd_rulebook.name, hit_dice from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join monster_movement_mode on dnd_monster.id=monster_id inner join dnd_racesize on size_id=dnd_racesize.id natural join carrying_capacity inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where intelligence<3 and constitution is null order by abbrev, speed, fine_biped_max_load_ounces*quadruped_carry_factor/3/16, -hit_dice;
  Huge|1040|f|50|Skirr|Libris Mortis: The Book of the Dead|9

Undead with tongues, such as ghouls and skirrs, actually retain their sense of taste.
Most diet-dependent undead can go for 3d6 months before losing all mobility. But mostly they must be satiated every three days, or make a DC 15 Will save.
A faint whirring sound and the stench of death precedes a great shape scudding through the air. The creature has a humanoid form with the skull of a long-toothed bull. Its upper arms are great wings, and its lower legs end in cruel, clawed talons. No skin or fur can be seen beneath the dingy gray funerary wrappings that cover the entire creature like a mummy.
Skirrs are predators that hunt the edges of necropolises, great expanses of deadly swamps, deserts, or other places where victims might be found alone, hurt, and pressed by dangers from directions other than the sky. That's when skirrs swoop in to attack.
Skirrs measure, wingtip-to-wingtip, 50 feet or more, and weigh about 20,000 pounds.
Skirrs know no languages.
It's...not clear where skirrs come from. The don't seem to be created, or spontaneously arise (no single living creature that fits the description "Huge humanoid with bull head and wings and talons"), or reproduce by assembling themselves from bits and pieces like skin kites.

Aside from the corpse-related creatures...well, the rust monster needs no introduction. "The touch can destroy
up to a 10-foot cube of metal instantly." The Down (DC 15) trick is obviously the most important one there.
A horse eats 10pounds of feed per day, costing 5cp. A rust monster probably doesn't eat ten pounds of iron per day, though. It just couldn't find that much in the wild. Pure iron is pretty hard to find for a creature without a burrow speed, and the thing about eating manufactured objects is that the owners tend to object...violently. In normal climates, Medium characters need at least a gallon of fluids and about a pound of decent food per day to avoid starvation. A pound of iron costs 1sp.
There actually are stats for larval rust monsters, in Complete Scoundrel. 160gp will buy you a 2-pound 1-foot-long piece of glass tubing about 4 inches in diameter that contains about a dozen rust monster larvae. Little more than 1 inch long and bristling with underdeveloped armor and appendages. Uncapping the solid cover and running the tip across a metal surface allows the hungry young to slowly but effectively eat through metal objects or barriers. The rust monster larvae in a wand can "ruin" a Large weapon or suit of armor (or a metal object of similar size) in 1 minute, but it's not clear how long it takes to actually eat through a barrier, since rendering a weapon or suit of armor unusuable doesn't require consuming it.
The larvae within a rust monster wand can survive for about 2 months if given air (by opening the outer layer of the end cap) and fed the equivalent of five coins of metal (or more) per day.
If removed from the wand, individual larvae do not have the size or ability to do appreciable harm to metal equipment. One of these creatures by itself has 1 hit point and can be crushed as a standard action.



Improved grabbers:

.. code-block:: bash

  sqlite> select distinct dnd_special_ability.name, (hit_dice*base_attack_per_4HD/4 + (strength - 10)/2 + (size_id - 5)*4) as grapple, dnd_monstertype.name, dnd_racesize.name, land_speed, dnd_monster.name, dnd_rulebook.name, 15 + hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstertype.name="Animal" or (dnd_monstertype.name="Magical Beast" and intelligence<3) ) and dnd_special_ability.name like "%improved grab%" order by DC, -grapple, size_id;
  Improved grab|6|Animal|Medium|20|Crocodile|Monster Manual v.3.5|18
  Improved grab|5|Animal|Medium|40|Leopard|Monster Manual v.3.5|18
  improved grab|5|Animal|Medium|20|Snake, Constrictor|Monster Manual v.3.5|18
  improved grab|5|Animal|Medium|20|Snake, Dung|Serpent Kingdoms|18
  improved grab|5|Animal|Medium|20|Snake, Whipsnake|Serpent Kingdoms|18
  Improved grab|7|Animal|Medium|30|Thudhunter|Arms & Equipment Guide|19
  Improved grab|14|Animal|Large|30|Lizard, Giant, Footpad|Drow of the Underdark|20
  Improved grab|16|Animal|Large|40|Bear, Brown|Monster Manual v.3.5|21
  Improved grab|21|Animal|Huge|20|Crocodile, Giant|Monster Manual v.3.5|22
  Improved grab|18|Animal|Large|40|Bear, Polar|Monster Manual v.3.5|23
  Improved grab|24|Animal|Huge|20|Lizard, Giant Banded|Sandstorm|25
  Improved grab|23|Animal|Large|40|Bear, Dire|Monster Manual v.3.5|27
  Improved grab|25|Animal|Huge|40|Megatherium|Fiend Folio|28
  Improved grab|30|Animal|Huge|40|Woolly Mammoth|Frostburn|29
  Improved grab|24|Animal|Large|40|Tiger, Dire|Monster Manual v.3.5|31
  improved grab|24|Animal|Large|30|Snake, Legendary|Monster Manual II|31
  Improved grab|35|Animal|Huge|50|Bear, Polar, Dire|Frostburn|33
  improved grab|40|Animal|Gargantuan|40|Dinosaur, Spinosaurus|Monster Manual II|35
  Improved grab|32|Animal|Large|50|Bear, Legendary|Monster Manual II|35
  Improved grab|34|Animal|Large|50|Tiger, Legendary|Monster Manual II|41
  improved grab|46|Magical Beast|Gargantuan|40|Lucent Worm|Fiend Folio|42
  Improved grab|51|Animal|Huge|40|Dinosaur, Battletitan|Monster Manual III|51


Interestingly, if we restrict to Large or smaller, there are no reversals; all Large animals or magical beasts are better grapplers than all Medium-size, which are in turn better grapplers than all Small.

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

...*except* for the Serpent Kingdoms sewerm.
This just goes to show that the database doesn't yet include racial bonuses. A sewerm has a +16 racial bonus on grapple checks, so although it's a Small animal, with 2HD and Str 17 it has total +16 to grapple checks. Also, anesthetic poison. Speed 20feet with climb and swim, just like other snakes.
A sewerm does not have Improved Grab, but unlike, say, a weasel, a sewerm's Attach ability is considered grappling.
Advancement: 3--4HD Medium, 5HD Large
The increase in size of Medium gives +4 Strength for a total of +6 to grapple checks. Its BAB also increases from +1 to +2, so a 3HD Medium sewerm has a total +23 to grapple checks.

Of course, an animal could in theory be trained to grapple even if it doesn't naturally do so. Sometimes, indeed, you don't actually want or need to damage the target in grappling them, if the purpose is capture.
If it is Huge or bigger, the Snatch feat grants Improved Grab for a claw or bite attack.
It's worth noting that some of the best grapplers already have Improved Grab anyway, such as the giant crocodile.

Advancement is unfortunately not in the database yet.
Since advancing from Medium to Large is worth +8 Strength for a total of +8 to grapple and trip checks, particularly large specimens might be more effective than species that are more commonly so large.
Advancement is usually not worthwhile for trippers, but for grapplers they get both the boost from size and strength and a boost from the hit dice.

.. code-block:: bash

  sqlite> select distinct (hit_dice*3/4 + (strength - 10)/2 + (size_id - 5)*4) as grapple, dnd_racesize.name, strength, dnd_monster.name, dnd_rulebook.name, 15 + hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where dnd_monstertype.name="Animal" order by DC, -grapple;
  2|Medium|15|Baboon|Monster Manual v.3.5|16
  2|Medium|14|Phynxkin|Dragon Magic|16
  4|Medium|16|Nifern|Serpent Kingdoms|17
    Advancement: +3=5HD Large
  3|Medium|14|Owl, Medium|Dungeon Master's Guide v.3.5|17
  3|Medium|15|Dog, Riding|Monster Manual v.3.5|17
  10|Large|18|Dinosaur, Cryptoclidus|Monster Manual II|18
  10|Large|18|Camel|Monster Manual v.3.5|18
  10|Large|18|Dinosaur, Pteranadon|Serpent Kingdoms|18
  13|Large|23|Drakkensteed|Dragon Magic|19
  12|Large|21|Ape|Monster Manual v.3.5|19
  12|Large|20|Jackal, Dire|Sandstorm|19
     Advancement +6=10HD Huge
  11|Large|18|Horse, Warhorse, Heavy|Monster Manual v.3.5|19
  11|Large|19|Lizard, Giant, Quicksilver|Drow of the Underdark|19
  11|Large|18|Camel, War|Sandstorm|19
  11|Large|19|Titan Salamander|Web|19
  14|Large|24|Advanced Nifern|Serpent Kingdoms|20
  14|Large|25|Lizard, Giant, Footpad|Drow of the Underdark|20
     Advancement +6=11HD Huge
  13|Large|22|Ape, Dire|Monster Manual v.3.5|20
  13|Large|22|Wolverine, Dire|Monster Manual v.3.5|20
  13|Large|22|Bison|Monster Manual v.3.5|20
  16|Large|27|Bear, Brown|Monster Manual v.3.5|21
  21|Huge|27|Crocodile, Giant|Monster Manual v.3.5|22  Improved grab
  20|Huge|24|Snake, Dire|Monster Manual II|22  Improved grab
     Advancement +6=13HD Gargantuan
  22|Huge|26|Dragonhawk|Five Nations|23
  24|Huge|28|Lizard, Giant Banded|Sandstorm|25
  27|Huge|33|Lizard, Giant, Footpad, Advanced|Drow of the Underdark|26
  19|Medium|30|Ape, Legendary|Monster Manual II|13
  55|Colossal|40|Dinosaur, Seismosaurus|Monster Manual II|32

Bigger animals are better at tripping...it helps to think of it not in terms of the word trip, but in terms of knocking someone prone ala the Awesome Blow feat.

For any given number of Hit Dice, the best trippers are exactly the best grapplers --- Hit Dice affects grappling while it doesn't affect tripping, but if we hold Hit Dice constant, that doesn't matter. On the other hand, the Animal type effectively gives five free Hit Dice, which makes animals more likely to be the best grapplers.

.. code-block:: bash

  sqlite> select distinct dnd_special_ability.name, ( (strength - 10)/2 + (size_id - 5)*4) as trip, dnd_monstertype.name, dnd_racesize.name, strength, dnd_monster.name, dnd_rulebook.name, hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstertype.name="Animal" or (dnd_monstertype.name="Magical Beast" and intelligence<3) ) and dnd_special_ability.name like "%trip%" order by trip, -DC, -size_id;
  Trip|2|Medium|15|Bat, Hunting|Monster Manual II|4
  Trip|2|Medium|14|Hyena|Monster Manual|2
    Advancement: +2=4HD Large
  Trip|3|Medium|16|Cheetah|Monster Manual|3
  Trip|3|Medium|17|War Mastiff|Heroes of Battle|3
  Trip|7|Medium|25|Wolf, Legendary|Monster Manual II|14
  Trip|9|Large|20|Jackal, Dire|Sandstorm|4
  An advanced wolf can equal a dire jackal, being Large with 4HD and Str21.
  Trip|11|Large|25|Wolf, Dire|Monster Manual|6
  Knockback|Brixashulty|Races of the Wild|2
  Knockback (Ex): A gore attack from a brixashulty can literally drive back a foe. When a brixa hits with its gore attack, it can immediately attempt a bull rush without entering the foe's space or provoking an attack of opportunity. The brixa makes a Strength check with a +7 bonus, which includes a +4 racial bonus. If the bull rush succeeds, the foe is driven back 5 feet and must make a DC 12 Reflex save or fall down. If being driven back would force the opponent into a barrier or into a square where it cannot stop (such as a wall or a square that already contains another creature), the foe falls down in its square instead.
  A brixashulty kid is worth 30 gp and is ready for training by age two. It can live for up to 50 years.
  A character with the Handle Animal skill can train a brixashulty as noted in the Handle Animal skill description

And of course an animal can trip without a special ability.
Note that an animal's trip bonus equals its bull rush bonus, which also equals its grapple bonus minus its base attack bonus.

.. code-block:: bash

  sqlite> select distinct ( (strength - 10)/2 + (size_id - 5)*4) as trip, dnd_monstertype.name, dnd_racesize.name, strength, dnd_monster.name, dnd_rulebook.name, 15 + hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where dnd_monstertype.name="Animal" and land_speed is not null order by DC, -trip;
  4|Medium|19|Bear, Black|Monster Manual|3
  4|Medium|19|Crocodile|Monster Manual|3
  8|Large|18|Camel|Monster Manual|3
  10|Large|22|Ape, Dire|Monster Manual|5
  10|Large|22|Bison|Monster Manual|5
  10|Large|23|Drakkensteed|Dragon Magic|4
  11|Large|25|Lizard, Giant, Footpad|Drow of the Underdark|5
  12|Large|27|Bear, Brown|Monster Manual|6
  16|Huge|27|Crocodile, Giant|Monster Manual|7

Bigger animals are better grapplers, but with smaller animals, more can dogpile on.

If your target is already grappling someone else, you can use an attack to start a grapple, as above, except that the target doesn't get an attack of opportunity against you, and your grab automatically succeeds. You still have to make a successful opposed grapple check to become part of the grapple.
If there are multiple opponents involved in the grapple, you pick one to make the opposed grapple check against.
Up to four combatants can grapple a single opponent in a given round. Creatures that are one or more size categories smaller than you count for half, creatures that are one size category larger than you count double, and creatures two or more size categories larger count quadruple.
When you are grappling with multiple opponents, you choose one opponent to make an opposed check against. The exception is an attempt to escape from the grapple; to successfully escape, your grapple check must beat the check results of each opponent.

Up to eight Small creatures can grapple one Medium target, whereas only four Medium creatures or two Large creatures or one Huge creature can do the same. Which is most difficult to escape? We can ask AnyDice.

.. code-block:: anydice

  output [highest 1 of 8d20] > [highest 1 of 4d20] + 6
  output [highest 1 of 4d20] + 6 > [highest 1 of 2d20] + 16
  output [highest 1 of 6d20] + 2 > [highest 1 of 3d20] + 4

Generally, the advantage of being larger dwarfs the advantage of being able to dogpile more. Not too surprising.





Unfortunately, without a source of data on feats, we cannot know which animals have the Track feat. On the other hand, Handle Animal might make the Track feat irrelevant: Track (DC 20): The animal tracks the scent presented to it. (This requires the animal to have the scent ability.)

.. code-block:: bash

  sqlite> select distinct dnd_special_ability.name, (wisdom - 10)/2, dnd_monstertype.name, dnd_racesize.name, dnd_monster.name, dnd_rulebook.name, hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstertype.name="Animal" or (dnd_monstertype.name="Magical Beast" and intelligence<3) ) and dnd_special_ability.name like "%scent%" order by wisdom/2, -DC;
  scent|1|Small|Dog|Monster Manual|1 has Track feat Dogs have a +4 racial bonus on Survival checks when tracking by scent.
  scent|1|Fine|Mouse|Dungeon Master's Guide v.3.5|-4 no Track feat
  scent|2|Small|Vulture|Sandstorm|1 has Track feat A vulture has a +4 racial bonus on Spot and Survival checks.
  scent|3|Medium|Bat, Hunting|Monster Manual II|4 ironically does not have the Track feat
  scent|3|Small|Dinosaur, Swindlespitter|Monster Manual III|2 no Track feat

complete adventurer p.100 Hunt (Handle Animal DC 15): The animal attempts to hunt and forage for food for you using its Survival skill. While any animal automatically knows how to hunt and forage for its own needs, this trick causes it to return with food rather than simply eating its fill of what it finds.
A deinonychus has a +8 racial bonus on Hide, Jump, Listen, Spot, and Survival checks.
A nashrou has no racial bonus, but does put max ranks in Survival by default.
Move up to one-half your overland speed while hunting and foraging (no food or water supplies needed). You can provide food and water for one other person for every 2 points by which your check result exceeds 10.

Just for fun, remember that Moonrats are indistinguishable from normal rats except in moonlight. If someone did use a rat as a tracker underground, it might turn out that Handle Animal stops working when it gets under the open sky, due to unexpectedly increased Intelligence...

.. code-block:: bash

  sqlite> select distinct dnd_special_ability.name, (wisdom - 10)/2, dnd_monstertype.name, dnd_racesize.name, land_speed, dnd_monster.name, dnd_rulebook.name, 15 + hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstertype.name="Animal" or (dnd_monstertype.name="Magical Beast" and intelligence<3) ) and (dnd_special_ability.name like "%sense%" or dnd_special_ability.name like "%sight%") order by dnd_special_ability.name, wisdom/2, -DC;
  Blindsight 100ft|2|Huge|20|Sea Tiger|Monster Manual III|10
  Blindsight 60ft|2|Medium|40|Nifern|Serpent Kingdoms|2
  Blindsense 120ft|3|Medium|20|Bat, Hunting|Monster Manual II|4
  Blindsense 60ft|2|Tiny|10|Chordevoc|Races of the Wild|1
  Blindsense 40ft|2|Large|20|Bat, Dire|Monster Manual|4
  Blindsense 20ft|2|Diminutive|5|Bat|Monster Manual|-4
  Blindsight 1200ft|5|Magical Beast|Gargantuan|50|Malastor|Monster Manual V|25
  Blindsight 120ft|2|Magical Beast|Small|10|Bakkas|Garden of the Plantmaster|6
  Blindsight 90ft|0|Magical Beast|Small|20|Darkmantle|Monster Manual|6
  Tremorsense 30ft|2|Magical Beast|Small|40|Gem Scarab, Diamond|Monster Manual V|22
  tremorsense 1200ft|5|Magical Beast|Gargantuan|50|Malastor|Monster Manual V|25
  tremorsense 60ft|1|Magical Beast|Medium|20|Thrum Worm|Races of Stone|7
  tremorsense 60ft|1|Magical Beast|Medium|30|Watchspider|City of Splendors: Waterdeep|22
  tremorsense 60ft|3|Magical Beast|Tiny|20|Tomb Spider, Broodswarm|Monster Manual IV|23
  tremorsense 60ft|0|Magical Beast|Small|30|Bloodsilk Spider|Monster Manual IV|22
  tremorsense 60ft|1|Magical Beast|Large|30|Ankheg|Monster Manual|8

`Chordevoc <http://archive.wizards.com/default.asp?x=dnd/ex/20050204a&page=5>`_
A halfling can train a chordevoc without penalty, but the Handle Animal DCs for any other trainer increase by 5.

Blindsight requires line of effect, but tremorsense does not.
If no straight path exists through the ground from the creature to those that it's sensing, then the range defines the maximum distance of the shortest indirect path.
It must itself be in contact with the ground, and the creatures must be moving. As long as the other creatures are taking physical actions, including casting spells with somatic components, they're considered moving; they don't have to move from place to place for a creature with tremorsense to detect them.

Unlike mundane or even monstrous vermin, bloodsilk spiders possess a cunning intelligence. They attack any living thing for its blood, using their webs to catch and slay even more prey. They are not powerful individually, so they prefer to attack in numbers, usually groups of four to eight.
A typical bloodsilk spider is about 3 feet long and weighs 40 to 50 pounds.

Watchspiders are fairly common in the cellars and warehouses of guild houses and rich merchants. They are trained to obey a single master, who can order them not to attack certain beings. Moreover, they can be trained so that most
attack while another rings an alarm bell or drinks from a basin containing a magic potion before joining a fight.
Watchspiders are indigenous to Tharsult, where the natives first trained the species as guards. The Mhairuun merchant family brought watchspiders and their breeding and training processes north to Waterdeep, swiftly establishing a lucrative business with this rare commodity. After sixty years of breeding in the North, watchspiders can be found in Sword Coast cities from Neverwinter to Lantan, all purchased and shipped from Waterdeep. While still a creature of more temperate climes, watchspiders have adapted to the Sword Coast with the growth of heavier hair (almost fur), but they still cannot survive the cold any further north than Neverwinter.

Trainable (Ex): A thrum worm is easier to train and handle than most other magical beasts. Handle Animal checks made to train or handle a thrum worm are not increased by 5. Gnomes receive a +2 circumstance bonus on all Handle Animal checks made to train or handle a thrum worm.
A thrum worm larva costs 1,500 gp on the open market

Hmm, I've always wondered, what is the intended use-case of the `Hover <http://www.d20srd.org/srd/monsterFeats.htm#hover>`_ feat?

.. code-block:: bash

  sqlite> select distinct challenge_rating, dnd_special_ability.name, dnd_monstertype.name, dnd_racesize.name, dnd_monster.name, dnd_rulebook.name, speed from dnd_monster inner join monster_movement_mode on monster_movement_mode.monster_id=dnd_monster.id inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where abbrev='f' and size_id>5 and (dnd_special_ability.name like "%sense%" or dnd_special_ability.name like "%sight%") order by challenge_rating, dnd_special_ability.name;
  2|Blindsense 40ft|Animal|Large|Bat, Dire|Monster Manual v.3.5|40

In theory a Medium-size creature could advance to Large size, but if you actually look at the blindsensers of Medium size who can fly, none of them fly with wings.
Of course since Hover doesn't obstruct sight at melee range, it doesn't really need blindsense...but the dire bat still pops up first anyway. (Though a 9HD Large cloaked ape CR 3 is also a possibility. There's also a 6HD Large sailsnake CR3, or a 9HD Large dire hawk CR3.)
Half-fiends have wings. A half-fiend Ur'Epona (probably spawned by an armanite) is CR 2 and a fairly serious threat in melee with its 1d6+5 claws and 1d8+2 bite and 1d6+2 hooves, plus DR 5/magic and SR13.

.. code-block:: bash

  sqlite> select distinct challenge_rating, dnd_monstertype.name, dnd_racesize.name, dnd_monster.name, dnd_rulebook.name, speed from dnd_monster inner join monster_movement_mode on monster_movement_mode.monster_id=dnd_monster.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where abbrev='f' and intelligence is not null and size_id>5 and challenge_rating<6 order by challenge_rating;
  2|Animal|Large|Bat, Dire|Monster Manual v.3.5|40

.. code-block:: bash

  sqlite> select distinct dnd_special_ability.name, 10 + hit_dice/2 + (constitution - 10)/2 as virulence, dnd_monstertype.name, dnd_racesize.name, land_speed, dnd_monster.name, dnd_rulebook.name, hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstertype.name="Animal" or (dnd_monstertype.name="Magical Beast" and intelligence<3) ) and (dnd_special_ability.name like "%poison%" or dnd_special_ability.name like "%venom%" or dnd_special_ability.name like "%drain%") and dnd_special_ability.name!="immunity to poison" and dnd_special_ability.name!="resistance to poison" order by virulence, -DC;
  poison|8|Diminutive|15|Hedgehog|Dungeon Master's Guide v.3.5|-4 Dexterity
  Poison|8|Tiny|10|Sea Snake, Tiny|Stormwrack|-4
  Poison|10|Small|10|Sea Snake, Small|Stormwrack|1 Constitution Poison (Ex): A sea snake's poison is extraordinarily virulent. It has a +2 racial bonus on the poison's save DC.
  Poison|10|Small||Stingray|Stormwrack|1 Poison (Ex): Injury, Fortitude DC 12, nauseated 1d4 hours/1d3 Dex. The save DC is Constitution-based and includes a +2 racial bonus. A creature that makes its saving throw against the poison's initial damage is instead sickened for 1d6 rounds. Blood Web (Ex) A bloodsilk spider can throw a blood-red web eight times per day. An entangled creature can escape with a DC 11 Escape Artist check or burst the web with a DC 15 Strength check. Both are standard actions and thus cannot be taken while nauseated, so a bloodsilk spider plus a stingray could keep someone contained for hours. Of course, you could just, you know, tie them up.
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
  Mlarraun 2HD Magical Beast Serpent Kingdoms Poison (Ex): spit, contact, Fortitude DC11, initial damage blindness 2d6hours, secondary damage blindness 4d6hours and 1d4 points of damage. The poison need not touch the eyes to cause blindness.


Mounts?

.. code-block:: bash

  sqlite> select distinct dnd_monstertype.name, dnd_racesize.name, fine_biped_max_load_ounces*quadruped_carry_factor/3/16 as light_load, land_speed, dnd_monster.name, dnd_rulebook.name, 15 + hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id natural join carrying_capacity inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstertype.name="Animal" or (dnd_monstertype.name="Magical Beast" and intelligence<3) ) order by land_speed, light_load, -DC;
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
  Large|15|65|Axebeak|Arms & Equipment Guide|3 Axebeaks move five times their normal speed when running instead of four times the speed. This is probably only noted as a special ability because animals didn't have feats in 3.0. Axebeak eggs are worth 20 gp on the open market. Note that axebeaks are bipeds, so cannot carry as much as the formula would indicate. An axebeak also cannot use a Tooth of Savnok after you can afford the 2,000gp, which allows other mounts to carry a medium or heavy load without slowing down. An axebeak is good for one thing and one thing only: outrunning pursuers by being just a *little bit faster* than a light horse, while not carrying much.
  Large|29|80|Horse, Legendary|Monster Manual II|18

The warbeast template, found by searching for templates below, adds +10 to land speed (maybe other speeds, it's not clear) and +3 Strength at the cost of 1HD. It also gains +3 to Constitution, so poisoners might benefit.
Speed: Same as base creature +10 feet.
Advancement: Same as base creature. So an animal will still increase in size at the same absolute HD count. Of course, advanced warbeasts are pricey.
A creature may become larger when its Hit Dice are increased (the new size is noted parenthetically in the monster's Advancement entry). Increased size also affects a creature's ability scores as indicated on the tables.
The warbeast is a creature born and raised to serve as a rider's mount. Bred for exceptional strength, aggression, and surefootedness, these creatures are powerfully built, strong-willed, and openly belligerent.
A warbeast can be reared and trained just as the base creature can. If the base creature is a domestic animal, the creature need not be specially reared, but it must be trained for two months (Handle Animal DC 20) to develop its abilities.
A warbeast based on a wild animal must be reared for one year (Handle Animal DC 15 + HD of the warbeast), then trained for 2 months (Handle Animal DC 20 + HD of the warbeast).
In 3.0, there were three categories of difficulty for Handle Animal: Domestic Animals, Wild Animals, and Beasts. Obviously, a Warbeast is always Domestic (in the D&D sense anyway if not the biological one). What that line says is that even though a Warbeast is domestic, it is still reared and trained as the base creature. If the base creature is a domestic animal, the warbeast is trained as a domestic animal. If it's a wild animal, it is trained as a wild animal. If it is a beast, it is trained as a beast. The DCs match, if you look up how 3.0 Handle Animal worked.
A trained warbeast is proficient with light, medium, and heavy armor.
Market Price: The market price of a warbeast is a function of its Hit Dice: 50 gp/HD for a warbeast of 3 HD or less, or 100 gp + 75 gp/HD for one of 4 HD or more.
A 100gp warbaboon has Str 18; a 100gp warphynxkin has Str 17. It's not clear whether they get a bonus to climb speed, however.
A 150gp warnifern has improved poison (and improved Strength).
A 150gp warhyena is even better at tripping. Gnolls probably use these.
A warbrixashulty kid probably costs 30gp + 150gp = 180gp.
A 150gp 3HD warsewerm has Str 17 + 3 + 4 = 24 since it increases in size to Medium, with a total grapple bonus of +25, and speed 30feet.

A dark dire warjackal costs 475gp and requires access to the Plane of Shadow, but has a speed of 80feet.
A dark waraxebeak costs 400gp and requires access to the Plane of Shadow, but has a speed of 85feet.

Of course, merchant caravans care about speed less than they care about efficiency of load-carrying.
Let's assume for the moment that size category can be a proxy for how much food and care an animal needs. Unfortunately, the database has no way to distinguish carnivores from herbivores, or quadrupeds from bipeds.
While the thought of a horde of skunks pulling a wagon is amusing, let's stick to animals that can individually carry more than a human.
We'll order by DC first, then carrying capacity, so that for any given level of Handle Animal available, we can look and see the best animal. Doing it this way, there is only any point in noting an animal at a higher DC if it is better in some way than the best option at a lower DC.

This might also be useful for a low-level druid trying to get the most out of Pass Without Trace --- a camel can carry 900 pounds, so one Pass Without Trace on the camel while it carries two or three party members gets more mileage.

.. code-block:: bash

  sqlite> select distinct dnd_monstertype.name, dnd_racesize.name, fine_biped_max_load_ounces*quadruped_carry_factor/3/16 as light_load, land_speed, dnd_monster.name, dnd_rulebook.name, 15 + hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id natural join carrying_capacity inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstertype.name="Animal" or (dnd_monstertype.name="Magical Beast" and intelligence<3) ) and light_load > 33 and size_id<6 order by DC, light_load, land_speed;
  Animal|Medium|87|40|Phynxkin|Dragon Magic|16
  Animal|Medium|100|40|Baboon|Monster Manual|16
  Animal|Medium|115|40|Nifern|Serpent Kingdoms|17
  Animal|Medium|75|40|Pony|Monster Manual|17 30gp
  Animal|Medium|50|30|Donkey|Monster Manual|17 8gp
  Animal|Medium|87|30|Donkey, Uglib|Champions of Valor|17
  Animal|Medium|100|40|Pony, War|Monster Manual|17 100gp
  Animal|Medium|130|40|Pony, Hammer|Champions of Valor|17
  Animal|Medium|130|40|Pony, Island|Champions of Valor|17
  Animal|Medium|130|40|Pony, Whiteshield|Champions of Valor|17
  Animal|Medium|100|40|Boar|Monster Manual|18
  Animal|Medium|100|40|Pig|Dangerous Denizens - The Monsters of Tellene|18
  Animal|Medium|175|40|Bear, Black|Monster Manual|18
  Animal|Medium|100|20|Bat, Hunting|Monster Manual II|19
  Animal|Medium|175|60|Dinosaur, Deinonychus|Monster Manual|19
  Magical Beast|Small|76|20|Darkmantle|Monster Manual|21
  Magical Beast|Medium|130|50|Elven Hound|Races of the Wild|22
  Magical Beast|Medium|150|20|Frog, Giant|Return to the Temple of Elemental Evil|23
  Animal|Medium|800|40|Ape, Legendary|Monster Manual II|28

  Animal|Large|230|30|Mule|Monster Manual|18 8gp
  Animal|Large|230|60|Horse, Warhorse, Light|Monster Manual|18 150gp
  Animal|Large|230|60|Horse, Light, Steppe|Champions of Valor|18
  Animal|Large|300|40|Camel, Two-Humped (Bactrian)|Sandstorm|18
  Animal|Large|300|50|Camel|Monster Manual|18
  Animal|Large|300|50|Camel, Dromedary|Sandstorm|18
  Animal|Large|300|50|Horse, Draft|Dangerous Denizens - The Monsters of Tellene|18
  Animal|Large|300|60|Camel, Racing|Dangerous Denizens - The Monsters of Tellene|18
  Animal|Large|350|40|Camel, Draft|Dangerous Denizens - The Monsters of Tellene|18
  Animal|Large|460|30|Ape|Monster Manual|19
  Animal|Large|600|50|Drakkensteed|Dragon Magic|19
  Animal|Large|520|40|Bison|Monster Manual|20
  Animal|Large|800|30|Lizard, Giant, Footpad|Drow of the Underdark|20
  Animal|Large|400|40|Megaloceros|Frostburn|21
  Animal|Large|1040|40|Bear, Brown|Monster Manual|21
  Animal|Large|800|50|Wolf, Dire|Monster Manual v.3.5|21
  Animal|Huge|2080|20|Crocodile, Giant|Monster Manual v.3.5|22
  Animal|Large|1040|40|Boar, Dire|Monster Manual|22
  Animal|Huge|2800|20|Dinosaur, Ankylosaurus|Monster Manual II|24
  Animal|Huge|3200|40|Elephant|Monster Manual v.3.5|26

The surprise standouts are boars and dire boars. Just as willing to eat foliage as the bodies of your fallen foes, they're strong and not too slow.
Raising a dire boar requires a total +12 if you take 10. A first-level human commoner with 4 ranks Handle Animal, +1 Charisma bonus, Skill Focus and Animal Affinity has +10, so they need Aid Another from an assistant. (The Uncivilized trait could give them a +1 bonus on Handle Animal checks, but that's not enough.)
Shape Soulmeld Riding Bracers are better than Skill Focus.
Killoren have a +2 racial bonus on Handle Animal checks; so do desert elves, but desert elves have a harder time managing the 13 Con needed for Shape Soulmeld.

A&EG 50gp Animal Trainer's Kit: This kit consists of harnesses, prods, light whips, treats, and other items that are helpful for training animals. There are different kits for different types of animals. It grants a +2 circumstance bonus on Handle Animal checks.
A&EG Leash and Muzzle: Made to fit creatures of various sizes, this is necessary equipment for training animals. Masterwork versions are also available that grant a +1 circumstance bonus on Handle Animal checks, increasing the price by 20 gp (regardless of size).
 only priced up to Medium-size 8sp
Frostburn page 76: "If you are proficient with its use, the goad grants a +2 circumstance bonus on all Handle Animal checks made against animals of Huge size or larger."
 Although many of these primitive weapons are categorized as exotic weapons, they can be used as martial weapons by those not trained in their use as exotic weapons. If a primitive exotic weapon is used as a martial weapon, the user cannot make use of any of that weapon's special qualities (such as the iuak's ability to damage objects, or the tigerskull club's ability to disarm and trip).
A&EG 10gp Animal Training Pole: This hollow pole has a strong, thin cord threaded through it and twisted into a loop at the end. When looped around an animal's neck, it provides an easy way to direct the animal while preventing the animal from moving any closer than the pole's length. An animal training pole provides a +2 circumstance bonus on attempts to teach an animal a task [but not to rear a wild animal].

A&EG Whip of Obeyance: This masterwork leather riding whip grants its user a +10 circumstance bonus on Handle Animal checks. This bonus applies only to creatures with Intelligence 2 or lower.
Caster Level: 5th; Prerequisites: Craft Wondrous Item, animal friendship; Market Price: 2,000 gp; Weight: 2 lb.

Bridle of Ease: This magic bridle grants trainers a +5 competence bonus on Handle Animal checks when training a *mount*. Versions of this item are available for exotic mounts.
Caster Level: 7th; Prerequisites: Craft Wondrous Item, charm monster; Market Price: 500 gp; Weight: 1 lb.
An animal can be trained for only one general purpose, though if the creature is capable of learning additional tricks (above and beyond those included in its general purpose), it may do so.
Riding (DC 15): An animal trained to bear a rider knows the tricks come, heel, and stay. Training an animal for riding takes three weeks.

Teamwork benefits require Int 8 for the leader, so a trained animal cannot be the leader.
You may have heard of the Team Rush teamwork benefit from the Player's Handbook II; that's the reason why, if you hitch an advanced 5HD shadow mastiff to a sled with a pack of regular dogs, they're inspired to move at the shadow mastiff's speed (50feet).
With the same teamwork training, an 8HD megaraptor can get a team of giant crocodiles or anklyosaurs to move at a speed of 60feet. Of course, if you can do that, you're close to getting elephants anyway.
More immediately, a 5HD advanced deinonychus can lead a team of Large giant footpad lizards at a speed of 60feet. (If you're restricted to Medium-size, then the heaviest-load-carrier up to DC20 *is* the deinonychus, so there's no point.)
Of course, drakkensteeds can haul almost as much as giant footpad lizards and move almost as fast as deinonychus, but drakkensteeds are expensive (15,000gp) and rare (thought to be a myth), whereas giant footpad lizards are known to be commonly used as mounts and dray animals. "Dwarves most often employ footpad lizards as mounts while they search new lodes of iron, mithral, and adamantine. These skilled climbers are best able to negotiate treacherous terrain."


What about other movement modes? For example, a tiny climber might be able to get your grappling hook where you need it more silently than you can.
Or maybe all you really want is a messenger eagle.

.. code-block:: bash

  sqlite> select distinct dnd_racesize.name, dnd_monstertype.name, fine_biped_max_load_ounces*quadruped_carry_factor/3/16 as light_load, abbrev, speed, dnd_monster.name, dnd_rulebook.name, 15 + hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join monster_movement_mode on dnd_monster.id=monster_id inner join dnd_racesize on size_id=dnd_racesize.id natural join carrying_capacity inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstertype.name="Animal" or (dnd_monstertype.name="Magical Beast" and intelligence<=2) ) order by abbrev, speed, light_load, -DC;
  Tiny|17|b|5|Lizard, Horned|Sandstorm|1
  Medium|87|b|10|Wolverine|Monster Manual|3
  Large|520|b|20|Dinosaur, Bloodstriker|Monster Manual III|9
  Large|Magical Beast|460|b|20|Ankheg|Monster Manual v.3.5|23
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
  Tiny|15|f|60|Hawk|Monster Manual v.3.5|1
  Small|33|f|80|Eagle|Monster Manual v.3.5|1
  Small|66|f|100|Eagle, Legendary|Monster Manual II|12
  Huge|1840|f|100|Dinosaur, Quetzelcoatlus|Monster Manual II|10

Bats have good maneuverability.

Training a pteranadon to bear a rider requires a DC 25 Handle Animal check, higher than normal. (Training a pteranodon to grapple, however, is no harder than normal.)

Unfortunately the database does not yet include skill ranks, so we cannot sort by the kinds of walls an animal can climb.

Hmm, the A&EG Riding Lizard seems to be missing from the database. But if it were actually in the database, it would be an example of something not caught by looking for a climb speed, because it does not have a listed climb speed of 20 feet, although it is given a climb speed of 20 feet by its spell-like ability.
Sticky Pads (Sp): A riding lizard has large, circular pads on its toes that exude adhesive. At will, a riding lizard can stick to any vertical or inverted surface as spider climb cast by a 20th-level sorcerer.
Large magical beast; HD 2d10+6; hp 17; Spd 40 ft.; Str 18, Dex 13, Con 17, Int 2, Wis 13, Cha 6.

Baboons can carry up to a hundred pounds, three hundred pounds if they accept moving slower.
Baboons have a +10 Climb modifier and can always take 10, so it can climb An uneven surface with some narrow handholds and footholds, such as a typical wall in a dungeon or ruins, but cannot climb a DC25 wall such as a natural rock wall or a brick wall.
Baboon Rock in Tanzania, Africa https://www.youtube.com/watch?v=42Px9N7jV7w&t=33s
(A phynxkin has only Climb +8, having allocated skill points to Hide and Move Silently? Something's wrong there, a phynxkin's Str 14 ought to be enough for Climb +10 on its own with no skill ranks.)

Burrowing is of questionable usefulness. A creature with a burrow speed can tunnel through dirt, but not through rock unless the descriptive text says otherwise. Most burrowing creatures do not leave behind tunnels other creatures can use.

40gp 25pound Saddle, Burrower's: This specialized exotic saddle allows the rider to stay safely on a mount that has the ability to burrow. The saddle includes a secure system of straps and buckles that holds the rider flush to the burrowing mount's back. In addition, a thick, round-edged piece of leather reinforced with bone or wood rises from the front of the shield, just before the rider's seat, roughly to the height of the rider's chest. The curved piece of leather bends up and toward the rider, allowing her to duck behind it while her mount burrows, shielding her from most of the dirt and rocks that might otherwise tear the rider from her perch, straps or no straps. Similar bits of reinforced leather protect the front and sides of the rider's legs.
 Strapping oneself to the saddle requires three consecutive full-round actions that provoke attacks of opportunity. Unbuckling the straps is a full-round action that provokes attacks of opportunity. While strapped into the saddle, you lose your Dexterity bonus to Armor Class and take a -4 penalty on all attack rolls.
 Weight given is for a saddle meant for a Large creature. Saddles made for Medium mounts weigh half this amount, and saddles made for Huge creatures weigh twice as much.

A burrowing ankheg usually does not make a usable tunnel, but can construct a tunnel; it burrows at half speed when it does so.
A frost worm cannot burrow through stone, but can manage ice and frozen earth. When moving through such hard materials it leaves behind a usable tunnel about 5 feet in diameter.
Dire badgers cannot burrow into solid rock, but can move through just about any material softer than that. A dire badger usually leaves behind a usable tunnel 5 feet in diameter when burrowing unless the material it's moving through is very loose. https://www.dailymail.co.uk/news/article-2120345/Residents-fear-homes-giant-badgers-dig-gardens-threatening-building-foundations.html


Technically, Handle Animal can work on any creature with an Intelligence score of 1 or 2 (which are also vulnerable to Ray of Stupidity), which technically includes any creature that has been Feebleminded, but making a creature friendly enough to be willing to be trained is a sticking point.
A druid can also use Wild Empathy to influence a magical beast with an Intelligence score of 1 or 2, but she takes a -4 penalty on the check.
Wild animals are usually unfriendly, http://www.d20srd.org/srd/classes/druid.htm#wildEmpathy
so it takes a DC15 check to make it indifferent, DC25 to make it friendly. A druid can also use this ability to influence a magical beast with an Intelligence score of 1 or 2, but she takes a -4 penalty on the check.


.. code-block:: bash

  sqlite> select distinct dnd_racesize.name, fine_biped_max_load_ounces*quadruped_carry_factor/3/16, abbrev, speed, dnd_monster.name, dnd_rulebook.name, hit_dice from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join monster_movement_mode on dnd_monster.id=monster_id inner join dnd_racesize on size_id=dnd_racesize.id natural join carrying_capacity inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where dnd_monstertype.name="Magical Beast" and intelligence<3 and abbrev='c' order by fine_biped_max_load_ounces*quadruped_carry_factor/3/16, -hit_dice, speed;
  No magical beasts make significantly better climbers than the best animals.


We can also search for templates with a final (not initial) type of animal:

.. code-block:: bash

  sqlite> select distinct dnd_template.name, dnd_rulebook.name, page from dnd_template inner join template_type on dnd_template.id=template_id inner join dnd_monstertype on dnd_monstertype.id=output_type inner join dnd_rulebook on rulebook_id=dnd_rulebook.id where dnd_monstertype.name="Animal";
  Half-Golem Will succeeded|Monster Manual II|209 -6 Int would kill an animal
  Dungeonbred Monster|Dungeonscape|112
  Warbeast|Monster Manual II|219
  Chameleon Creature|Underdark|83
  Dark Creature|Tome of Magic|158
  Kord-Blooded|Monster Manual V|66
  Mineral Warrior|Underdark|96
  Voidmind Creature|Monster Manual III|187 Int +2
  Woodling|Monster Manual III|197

(There are no templates that turn something into an Animal that wasn't an Animal before. Same for the Vermin type.)

.. code-block:: bash

  sqlite> select distinct dnd_template.name, dnd_rulebook.name, page from dnd_template inner join template_type on dnd_template.id=template_id inner join dnd_monstertype as output on output.id=output_type inner join dnd_monstertype as input on input.id=base_type inner join dnd_rulebook on rulebook_id=dnd_rulebook.id where output.name="Animal" and input.name!="Animal" order by dnd_rulebook.name;
  sqlite> select distinct dnd_template.name, dnd_rulebook.name, page from dnd_template inner join template_type on dnd_template.id=template_id inner join dnd_monstertype as output on output.id=output_type inner join dnd_monstertype as input on input.id=base_type inner join dnd_rulebook on rulebook_id=dnd_rulebook.id where output.name="Vermin" and input.name!="Vermin" order by dnd_rulebook.name;


Dungeonbred is an inherited template that can be applied to any living corporeal aberration, animal, magical beast, or vermin that is Large or bigger.
Size and Type: The size of the creature is reduced one step, so that a Large base creature becomes a Medium dungeonbred monster.
Easy Maintenance (Ex): Dungeonbred monsters consume food and water as if they were one size smaller than they actually are (and thus two sizes smaller than the base creature).
Abilities: Increase from the base creature as follows: Str +4, Con +4. Since a dungeonbred monster is reduced in size from the base creature, remember to adjust its ability scores appropriately: -8 Str and -4 Con (so on net -4 Str), usually +2 Dex, and loss of some natural armor.

A chameleon creature has a climb speed equal to one-half its highest nonflying speed.
Of course, it's not likely to be a better climber than an ape or a forest sloth. And very high speeds tend to be swim speeds anyway, and those animals tend to be Aquatic, which means they won't really get to use that climb speed unless they're amphibious.
The chameleon template does, however, allow an animal that has only a swim speed (yet can breathe air) to function on land.

.. code-block:: bash

  sqlite> select distinct dnd_monstersubtype.name, dnd_racesize.name, fine_biped_max_load_ounces*quadruped_carry_factor/16 as maxLoad, abbrev, speed, dnd_monster.name, dnd_rulebook.name, 15 + hit_dice + CASE dnd_monstertype.name WHEN "Animal" THEN 0 ELSE 5 END as DC from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join monster_movement_mode on dnd_monster.id=monster_movement_mode.monster_id inner join dnd_racesize on size_id=dnd_racesize.id natural join carrying_capacity inner join dnd_rulebook on dnd_rulebook.id=rulebook_id left join monster_has_subtype on monster_has_subtype.monster_id=dnd_monster.id left join dnd_monstersubtype on subtype_id=dnd_monstersubtype.id left join monster_has_special_ability on monster_has_special_ability.monster_id=dnd_monster.id left join dnd_special_ability on special_ability_id=dnd_special_ability.id where dnd_monstertype.name="Animal" and abbrev="s" and (dnd_monstersubtype.name is null or dnd_monstersubtype.name!="Aquatic" or dnd_special_ability.name like "%Amphibious%") order by speed, maxLoad, -DC;
  Medium|57|s|80|Porpoise|Monster Manual|2

Similarly, a mineral warrior gains a burrow speed equal to one-half the base creature's highest speed.
Of course, mineral warriors are rare and expensive to create.

The Plane of Shadow boasts dark reflections of just about every race to populate the Material Plane.
Dark creatures dwell on the Plane of Shadow, sometimes crossing into other planes where the barriers between dimensions are weak. Just as parts of the Plane of Shadow resemble a strange, distorted version of the Material Plane, dark creatures superficially resemble creatures from the Material Plane.
Gray and black are their most common colors, and they almost never boast bright hues such as white or yellow.
Dark is an acquired or inherited template that can be added to any creature (referred to hereafter as the base creature).
Dark creatures tend to be much duller in color, with more gray and black skin tones and hair highlights, than their Material Plane versions. In general, they also weigh less, as if part of their very substance was mere shadow stuff.
Speed: As base creature, +10 feet to all modes of movement.
Resistance to cold 10, which might matter for otherwise-tropical animals.
Environment: Changes to Plane of Shadow.
Alignment: Usually one step different from the base creature, rarely good. The example dark lion is usually neutral evil.

A dark crocodile has a land speed of 30feet, making it much more viable. Of course, a dark crocodile is almost definitely going to be neutral evil.

Kord-blooded is an acquired template that can be added to any non-evil living creature that has a Strength score of 16 or higher.
Each year, the major temples to Kord hold a great wrestling tournament, and the tournament's winner wrestles an aspect of Kord. Whoever pins the other wins.
Kord's Athleticism (Su): Once per day, as a swift action, a Kord-blooded creature can call upon the blood invested in him to gain a tremendous surge of prowess. For the next minute, the Kord-blooded creature gains a +4 bonus on Strength and Dexterity checks, Strength- and Dexterity-based skill checks, and grapple checks.

Kord-blooded is of benefit to trippers, but obviously it's most appropriate for grapplers.

A 3HD woodling can use Summon Nature's Ally II to summon an elemental.

.. code-block:: bash

  sqlite> select distinct dnd_template.name, dnd_rulebook.name, page from dnd_template inner join template_type on dnd_template.id=template_id inner join dnd_monstertype on dnd_monstertype.id=output_type inner join dnd_rulebook on rulebook_id=dnd_rulebook.id where dnd_monstertype.name="Magical Beast" order by dnd_rulebook.name;
  Chimeric or Ti-khana creatures get Int +2. Quorbound or quorbred creatures get Int +4.
  Living Zombie|Champions of Ruin|128
  Half-Golem Will succeeded|Monster Manual II|209

Half-golem is a template that can be added to any animal, beast, giant, humanoid creature, magical beast, or monstrous humanoid.
Abilities: Half-golems have -2 Dex, +4 Con (or no Con upon a failed Will save), -6 Int, +0 Wis, and -6 Cha.
Wound (Ex): The damage a clay half-golem deals doesn't heal naturally. Only a spell of 6th level or higher with the healing descriptor (such as heal) can repair it. But the 3.5 update says: See Monster Manual for revised golem special attacks (note the change to clay golem's cursed wound).
A clay limb must be sculpted from a single block of clay weighing at least 100 pounds. The sculpting requires a successful Craft (sculpting) or Profession (mason) check (DC 20). The rituals cost 12,000 gp and 240 XP and require animate objects and geas/quest. Attaching the limb requires the ability to cast 6th-level divine spells.

Lost is an acquired template that can be added to any living creature with an Intelligence score of at least 3.
A lost's type does not change, but it gains the incarnum subtype.
The creature's base land speed increases by 10 ft. Any swim, fly, or burrow speeds the base creature might have do not increase.
Song of Misery (Ex): As a free action, a miserable lost can begin a droning song. Every creature within 30 feet who can hear it is fascinated for as long as the song continues, plus 1 round thereafter (Will negates).
But a miserable lost might not be the best to train --- a despairing lost might be less likely to rebel.
Twisted Mind (Ex): A lost's mind is demented and difficult to control. If the creature fails its saving throw against a mind-affecting spell or effect, it can attempt to save again 1 round later at the same DC. The lost gets only this one extra chance to succeed on its saving throw.
Abilities: Alter from the base creature as follows: Str +4, Con +4, Int -6 (minimum 1). If the lost's Intelligence score falls to 2 or 1, the creature regresses to an animal state and commences living off the wild as best it can.
Organization: Any.
Challenge Rating: Same as the base creature +1.
Alignment: Always evil (any).
If an infected creature takes 6 or more points of Intelligence damage while within the bounds of a lost site, the creature immediately gains the lost template described on page 183. Only living creatures with an Intelligence score (before disease damage) of at least 3 are at risk of becoming lost.

A living zombie's Intelligence changes to 1.
Creating a living zombie costs 1,000 gp in materials.
It is unable to act contrary to its creator's wishes. A spellcaster can concurrently control at most one living zombie per ability point bonus in primary spellcasting ability.





What about hirelings? Maybe what you really need is for someone to dangle a rope down into the chasm, and when you come running out of the dungeon in the "Get to the choppa!" moment, pull you up leaving your pursuers behind. For that, animals just won't do.

.. code-block:: bash

  sqlite> select distinct law_chaos, dnd_monstertype.name, dnd_racesize.name, strength, fine_biped_max_load_ounces*biped_carry_factor/16, land_speed, dnd_monster.name, intelligence, dnd_rulebook.name, challenge_rating from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id natural join carrying_capacity inner join dnd_rulebook on dnd_rulebook.id=rulebook_id inner join monster_has_alignment on dnd_monster.id=monster_has_alignment.monster_id where intelligence>=3 and challenge_rating<2 order by fine_biped_max_load_ounces*biped_carry_factor, challenge_rating, law_chaos;
  L|Humanoid|Small|9|67|30|Kobold|10|Monster Manual|-4
  L|Aberration|Tiny|14|87|5|Cerebral Symbiont, Psionic Sinew|6|Fiend Folio|-8
  L|Humanoid|Medium|10|100|20|Mongrelfolk|9|Fiend Folio|-3
  L|Humanoid|Medium|14|175|20|Skarn|10|Magic of Incarnum|-2
  N|Humanoid|Medium|15|200|20|Neanderthal|8|Frostburn|-2
  C|Humanoid|Medium|17|260|30|Orc|8|Monster Manual|-2
  L|Outsider|Medium|15|200|30|Planetouched, Zenythri|10|Monster Manual II|1
  N|Giant|Medium|15|200|30|Half-Giant|10|Expanded Psionics Handbook|1 http://www.d20srd.org/srd/psionic/monsters/halfGiant.htm
  L|Monstrous Humanoid|Large|12|260|30|Naga, Shinomen, Chameleon|13|Oriental Adventures|1
  N|Humanoid|Large|13|300|30|Saurial, Hornhead|12|Serpent Kingdoms|1

Honorable mention for portability goes to the psionic sinew, though it's not very mobile on its own so you'll need to do most of the work of setting it up to do its job. Something that small (yet strong) is easy to transport and hide.
A psionic sinew is blind, but its entire body is a primitive sensory organ that can ascertain prey by scent and vibration. This ability enables it to discern objects and creatures within 60 feet.
Share Spells (Su): Any spell the host creature casts on itself automatically also affects the symbiont. The host and symbiont can share spells even if the spells normally do not affect creatures of the host or symbiont's type. Spells targeted on the host by another spellcaster do not affect the symbiont, and vice versa.
Unlike with familiars, the spell does not automatically end if the symbiont detaches from the host, so in theory a psionic sniew could be Enlarge Personed, but the duration is likely too short to be useful.
Treasure: None. A psionic sinew does not speak any language, but it understands Undercommon. Usually lawful evil. It's not particularly clear what the worm *wants*, really.

Mongrelfolk are an excellent bargain choice. Often Lawful Neutral, with -2 Int and -4 Cha, they tend towards following rather than leading, but they're still more than smart enough to follow complex instructions.
Mongrelfolk are also particularly poor.
Treasure: 50% coins, standard goods, 50% items

Treasure values are not integrated into the database yet, so we'll have to do this by hand for now.
EL1 has an average of 0.05*25=1.25 platinum pieces, 0.52*90=46 gold pieces, 0.23*450=103.5 silver pieces, and 0.15*3,500=525 copper pieces, for a total of 12.5 + 46 + 10.35 + 5.25 = 58.5 + 15.6 = 74.1gp.
EL1 has a 5% chance of 1 gem plus a 5% chance of 1 art, total 275/20 + 55 = 13.75 + 55 = 68.75gp.
EL1 has a 0.24 probability of 1 mundane item plus a 5% chance of 1 minor magic item, total 0.24*350 + 1,000/20 = 84 + 50 = 134gp.
The CR 1/3 mongrelfolk cuts all of those by a factor of 3 to start with (because three randomly-chosen mongrelfolk would be an EL1 encounter), and then cuts the coins and items in half again (for the coins that means half as many coins, for the items that means half the chance, per the Monster Manual).
That leaves the mongrelfolk with 12.35gp in coins, 22.92gp in goods, and 22.33gp in items. And remember, that's an average. Some mongrelfolk have much less. They're cheap hires, is what I'm saying. This might have something to do with the fact that even the Fiend Folio narrator seems prejudiced against them.

Mongrelfolk speak Common and their own pidgin language.
Mongrelfolk are extremely cowardly, and they avoid direct conflict as much as possible. If we're talking about first-level Commoners hired as porters for adventurers, cowardice and common sense are basically the same thing. They construct traps around their lairs rather than relying on combat to keep intruders away. I like these folks already.

They have average strength but +4 Con, so you don't need to worry about their endurance; they'll outlast you.
Speed: 20 ft. (hide armor); base 30 ft.

A note of caution. Just because someone says he's a first-level Commoner doesn't mean he *is* a first-level Commoner. And "Often Lawful Neutral" doesn't mean the mongrelfolk in front of you is Lawful. A mongrelfolk's favored class is rogue. Mongrelfolk have a +8 racial bonus on Hide and Sleight of Hand checks. So, you know. Detect Law is your friend. Detect Evil wouldn't be a bad idea either.

Sound Imitation (Ex): A mongrelfolk can mimic any voice or sound it has heard. Listeners must succeed on a Will save (DC 16) to detect the ruse.

Neanderthals, orcs, and skarns all cost about as much to hire as humans. They offer enhanced strength, but are hard to find (neanderthals) or hard to find trustworthy people among (orcs) or hard to convince to leave the city (skarns). The advantage is that the stronger each porter is, the fewer you have to bring (and protect).

Neanderthals, stunningly, have Treasure: Standard. Neanderthals speak Common. Often neutral.
A neanderthal's base land speed is 30 feet. +2 Strength, +2 Constitution, -2 Intelligence.

Skarns have +2 Strength. Skarn base land speed is 30 feet. Skarns speak Common.
Skarns are usually lawful. They count an equal number of adherents to the ethos of good and evil among their race, but chaotic skarns are rare. The hierarchical skarn society features clearly defined social classes.
With a height of about 6 feet and a weight of approximately 210 pounds, a typical skarn is signifi cantly more massive than an average human. Skarns adorn their spines with jewelry, and even in everyday circumstances they keep these natural weapons polished and sharp.

Orcs are Often chaotic evil, so you might have a bit of a job finding a Lawful one, especially if you want Lawful Neutral rather than Lawful Evil. Treasure: Standard.

Zenythri have +2 Strength, -2 Charisma.
Half-giants have +2 Strength.

A saurial hornhead can lift as much as any three mongrelfolk, but they're expensive, hard to communicate with, and too big to be transported conveniently.
Saurial hornheads have +2 Strength...and +2 Intelligence, so don't underestimate them. Treasure: Standard. Usually neutral good.
Hornheads tend to be careful, rational planners. They choose their words carefully and avoid taking action without prior contemplation. Most are interested in alchemy, engineering, and other mental pursuits, and many also enjoy physical tasks requiring discipline, such as blacksmithing and weaponsmithing.
Most adventuring hornheads are consumed by a desire to understand the particulars of the world around them. Some choose to study the laws of other cultures, some the philosophical underpinnings of a religion, and some the arcane secrets of new spells. A hornhead's favored class is wizard, although some choose to develop an innate talent for sorcery instead.
Hornheads speak Draconic. They understand (but do not speak) Common, Elven, Sylvan, and Celestial.
Automatic Languages: Draconic. Bonus Languages: Common, Elven, Sylvan, and Celestial. Hornheads have difficulty with other languages. Although they can understand and read all the bonus languages they know, they cannot speak them without spending skill points.
Hornhead base speed is 30 feet.
This bipedal lizard is as big as an ogre and has a tail longer than its own body.

Maybe you don't need somebody strong, though. Maybe you just need someone who's easy to carry, easy to hide, and can do basic tasks like trip the spring on a cablespool. The obvious answer is a small female halfling commoner. Is there a better answer?

.. code-block:: bash

  sqlite> select distinct law_chaos, dnd_monstertype.name, dnd_racesize.name, strength, fine_biped_max_load_ounces*biped_carry_factor/16, land_speed, dnd_monster.name, intelligence, dnd_rulebook.name, challenge_rating from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join dnd_racesize on size_id=dnd_racesize.id natural join carrying_capacity inner join dnd_rulebook on dnd_rulebook.id=rulebook_id inner join monster_has_alignment on dnd_monster.id=monster_has_alignment.monster_id where intelligence>=3 and size_id<5 and challenge_rating<2 order by challenge_rating, size_id, law_chaos;
  L|Monstrous Humanoid|Tiny|4|20|20|Muckdweller|10|Serpent Kingdoms|-4
  L|Humanoid|Small|9|67|30|Kobold|10|Monster Manual|-4
  C|Plant|Small|8|60|20|Twig Blight|5|Monster Manual II|-3
  C|Humanoid|Small|10|75|30|Tasloi|10|Shining South|-3
  C|Humanoid|Small|11|86|30|Xvart|10|Dragon Magazine|-3
  N|Humanoid|Small|11|86|30|Goblin|10|Monster Manual|-3
  C|Outsider|Tiny|7|35|20|Gen, Air|13|Dragon Magazine|-2
  C|Outsider|Tiny|9|45|20|Gen, Earth|13|Dragon Magazine|-2
  L|Plant|Tiny|8|40|20|Myconid, Junior Worker|9|Monster Manual II|-2
  N|Fey|Tiny|3|15|40|Jermlaine|8|Monster Manual II|-2
  N|Construct|Diminutive|1|2|20|Homunculus, Expeditious Messenger|8|Eberron Campaign Setting|-3
  N|Construct|Tiny|8|40|50|Homunculus, Furtive Filcher|12|Eberron Campaign Setting|-2
  N|Construct|Tiny|8|40|10|Homunculus, Arbalester|12|Magic of Eberron|-2
  N|Construct|Tiny|8|40|50|Stone Spirit, Tiny|8|Oriental Adventures|-2
  L|Construct|Small|10|75|20|Warforged, Scout|9|Monster Manual III|-2
  N|Construct|Tiny|8|40|20|Homunculus|10|Monster Manual|1
  N|Dragon|Tiny|6|30|15|Pseudodragon|10|Monster Manual|1
  N|Fey|Tiny|5|25|20|Sprite, Grig|10|Monster Manual|1
  N|Construct|Tiny|7|35|20|Bogun|8|Monster Manual II|1
  N|Fey|Tiny|3|15|15|Petal|15|Monster Manual III|1
  L|Plant|Small|11|86|20|Myconid, Average Worker|10|Monster Manual II|1
  N|Elemental|Small|17|195|20|Elemental, Earth, Small|4|Monster Manual|1
  N|Construct|Small|16|172|30|Homunculus, Packmate|8|Magic of Eberron|1

Muckdwellers are usually lawful evil. Many serve kuo-toa or lizardfolk tribes, surviving on the periphery and venerating their gods. Muckdwellers speak Draconic.
bipedal creature that resembles an upright Gila monster. A muckdweller looks like a miniature bibedal dinosaur with mottled gray and brown scales and a pale yellow underbelly. Its short tail is used for balancing and swimming. It has partially webbed feet and small, weak, prehensile foreclaws.
Though they are not tool users, they do occasionally build rafts of weeds, twigs and mud on which to float and hunt, as well as shelters where they can hide from predators. Treasure: Standard. Int 10, Wis 9, Cha 8.
Muckdwellers hibernate during the winter months in temperate or colder climes.
Be warned, because of theor meed fpr warmth, they'll probably want to share your bedroll.

A kobold is 2 to 2-1/2 feet tall and weighs 35 to 45 pounds. Kobolds don't offer much in the way of advantages over halflings.

In the desert, elves follow nomadic lifestyles. They herd horses, cattle, and goats across the sands, sleeping during the day and working or traveling at night. Their wandering takes them many places and puts them in contact with many cultures. As a result, they are welcome everywhere for the news and exotic trade goods they carry. Though they don't carry much with their -2 Strength; they have animals carry for them.
+2 racial bonus on Handle Animal and Ride checks: Desert elves spend most of their lives riding and working with animals. Elves average 5 feet tall and typically weigh just over 100 pounds.
Goblins have a +4 racial bonus on Move Silently and Ride checks, so a goblin can use its mount as cover with a DC15 Ride check, make leaps, and spur mounts. A goblin stands 3 to 3-1/2 feet tall and weighs 40 to 45 pounds.
Halflings stand about 3 feet tall and usually weigh between 30 and 35 pounds. Female halflings can be as small as 2'8" and 27pounds.
Forest gnomes average 2 to 2-1/2 feet in height; gnomes' weight generally goes up or down by 1 pound per inch of height; so a 2-foot female forest gnome might weigh only 25pounds.

You don't hire a homunculus; you build one. A homunculus cannot be created until almost the level where you could have skeletons, but unlike skeletons, a homunculus is intelligent. Craft Construct (see page 303), arcane eye, mirror image, mending, caster must be at least 4th level; Price - (never sold); Cost 1,050 gp + 78 XP.
The creator must be at least 7th level and possess the Craft Wondrous Item feat to make a bogun.

A warforged scout stands about 3 feet tall and weighs 60 pounds. Warforged scouts speak the language of their
creators, usually Common. Often lawful neutral.
Just as the warforged strive to find a place in society in times of peace, they simultaneously struggle to find ways to relate to the races that created them. In general, the humanoid races regard the warforged as an unpleasant reminder of the brutality of war and avoid dealing with them when possible. Some societies regard them as the property of the military forces that paid to have them built, and most warforged in those lands serve as slave laborers. In other lands, they are free but sometimes the victims of discrimination, hard-pressed to fi nd work or any kind of acceptance. Most warforged, not particularly emotional creatures, accept their struggles and servitude with equanimity, but others seethe with resentment against all other races as well as those warforged whose only desire is to please their masters.

Petals often act as servants, messengers, or attendants to larger or more prestigious fey including sprites and dryads. When not in service to another fey, they tend to cluster near some more powerful plant creature (such as a treant) for protection.
Petals are fast flyers, so are somewhat capable of keeping themselves safe.
A typical petal stands 1-1/2 feet tall and weighs 3 pounds.
Petals speak Sylvan and Common. Usually neutral good. Treasure: Standard. Level Adjustment: +2 (cohort)

A few jermlaines can speak Common, Dwarf, Gnome, Goblin, or Orc, but seldom can any individual speak more than one of those languages.
Myconids do not speak, and only CR2 elder workers and above can communicate telepathically.

That brings up another question. Traditionally, the way to communicate with people when you don't share a common language is to employ a translator. But when your job of boldly going where no man has gone before takes you to isolated tribes, that isn't terribly practical. Any adept or cleric can Comprehend Languages, but for two-way communication you need two of them, each sharing a common language with one side.
...*or* you can employ a *universal* translator.

.. code-block:: bash

  sqlite> select distinct law_chaos, dnd_monster.name, challenge_rating, dnd_rulebook.name, intelligence from dnd_monster inner join monster_has_special_ability on dnd_monster.id=monster_has_special_ability.monster_id inner join dnd_special_ability on monster_has_special_ability.special_ability_id=dnd_special_ability.id inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id left join monster_has_subtype on dnd_monster.id=monster_has_subtype.monster_id left join dnd_monstersubtype on monster_has_subtype.subtype_id=dnd_monstersubtype.id inner join monster_has_alignment on dnd_monster.id=monster_has_alignment.monster_id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstersubtype.name="Tanar'ri" or dnd_monstersubtype.name="Baatezu" or dnd_monstersubtype.name="Angel" or dnd_monstersubtype.name="Archon" or dnd_monstersubtype.name="Demodand" or dnd_monstersubtype.name="Yugoloth" or dnd_monstersubtype.name="Eladrin" or dnd_monstersubtype.name="Loumara" or dnd_monstersubtype.name="Obyrith" or dnd_monstersubtype.name="Symbiont" or dnd_special_ability.name like "%telepathy%" or dnd_special_ability.name like "%tongues%" or dnd_special_ability.name like "%language%") and challenge_rating<=2 order by (challenge_rating);
  Cerebral Symbiont, Mind Leech|-8|Fiend Folio|16
  Puppeteer|1|Expanded Psionics Handbook|14 http://www.d20srd.org/srd/psionic/monsters/puppeteer.htm
  Fiendish Symbiont, Soul Tick|-8|Fiend Folio|14
  Naga, Shinomen, Greensnake|-2|Oriental Adventures|11
  Pseudodragon|1|Monster Manual|10
  Sheengrass Swarm|1|Web|5 http://archive.wizards.com/default.asp?x=dnd/psb/20040521d
  Demon, Mane|1|Fiendish Codex I|3
  Archon, Lantern|2|Monster Manual|6
  Demon, Dretch|2|Monster Manual|5
  Eladrin, Coure|2|Book of Exalted Deeds|12
  X|Protectar|2|Miniatures Handbook|10
  N|Dabus|2|Expedition to the Demonweb Pits|12

Telepathy (Su): A mind leech can communicate telepathically with its host, if its host has a language.
Attach (Ex): If a mind leech hits with its bite attack, it burrows into the target's flesh and makes its way to the brain stem. Since the bite deals no damage and the leech secretes an anesthetic, the host is often unaware it has been bitten until the mind leech has established itself at the seat of the host's central nervous system.
a mind leech has a base Ego score of 8 (Int 16, Wis 14, Cha 16), plus 2 for its mind blast special attack, 4 for its psionic abilities of charm monster and suggestion, 1 for its detect thoughts psionic ability, and 1 for its telepathy, for a total Ego of 16.
Using a mind leech as a babelfish is a white-knuckle maneuver, since a mind leech can seize control of the host with its psionic abilities without regard to Ego.
A puppeteer can translate without needing to seize a host. On the other hand, a puppeteer can Charm people without needing to seize a host.

When characters with fiendish symbionts interact with nonevil NPCs, a -6 circumstance penalty is applied on all Charisma-based checks (Diplomacy, Bluff, and so on).

A sheengrass swarm is a very interesting option, but it sounds like a sheengrass swarm cannot be carried, and while its land speed of 30feet is respectable, its range is limited.
Earth Root (Ex): A sheengrass swarm can travel only on soft natural ground (such as soil or earth, but not stone).

Pseudodragons are a trap: when you go to look at the actual ability text, it doesn't work like other Telepathy abilities.
Telepathy (Su): Pseudodragons can communicate telepathically with creatures that speak Common or Sylvan, provided they are within 60 feet.

Telepathy (Ex): Nagas are all part of a communal consciousness they call the Akasha. This shared consciousness facilitates communication between nagas near and far, and contains the memories of their entire species. A group of nagas within 30 feet of each other are in constant communication.

A possessing fiend can, at any time, speak mentally to the creature it possesses in a language that creature can understand, although if the victim isn't very intelligent, its comprehension might be limited.
A possessing fiend has immediate access to all of its victim's current thoughts, as though using the detect thoughts spell, except that it automatically reads surface thoughts. If desired, a possessing fiend can probe the possessed creature's memories as well, but the victim is allowed a Will save.

If you have access to the Outer Planes, you have a lot of options. If you're confined to the Material Plane, you basically have the Coke-or-Pepsi choice of mind leech or puppeteer. Puppeteers can only charm humanoids, so there's that. Both Lawful Evil, both highly intelligent. If you successfully form an alliance --- good luck with that --- they probably won't outright betray you, but you'll be trusting a highly intelligent evil creature to tell you what people are saying and tell other people what *you* are saying. Oh, and in the case of the mind leech, you have to convince people to allow the mind leech into their brains before you can communicate with them.

It's worth mentioning that a mane, dretch, coure, lantern archon, or protectar can also take the Mindsight feat to sense creatures within 100 feet.

There is another way to "communicate".
A commanded undead creature is under the mental control of the evil cleric. The cleric must take a standard action to give mental orders to a commanded undead.

.. code-block:: bash

  sqlite> select distinct dnd_monster.name, intelligence, dnd_monstertype.name, dnd_monstersubtype.name, dnd_racesize.name, hit_dice, dnd_rulebook.name from dnd_monster inner join dnd_monstertype on dnd_monstertype.id=dnd_monster.type_id left join monster_has_subtype on dnd_monster.id=monster_has_subtype.monster_id left join dnd_monstersubtype on subtype_id=dnd_monstersubtype.id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstertype.name="Undead" or dnd_monstertype.name="Dragon" or dnd_monstertype.name="Plant" or dnd_monstertype.name="Elemental" or dnd_monstersubtype.name="Air" or dnd_monstersubtype.name="Earth" or dnd_monstersubtype.name="Fire" or dnd_monstersubtype.name="Water" or dnd_monster.name like "%Naga%") and intelligence>=3 and hit_dice<=1 order by hit_dice, dnd_monstertype.name, dnd_rulebook.name;
  Myconid, Junior Worker|9|Plant|Tiny|1|Monster Manual II
  Twig Blight|5|Plant|Small|1|Monster Manual II
  Volodni|8|Plant|Medium|1|Unapproachable East
  Ghostly Visage|12|Undead|Tiny|1|Fiend Folio
  Little Thing|8|Undead|Small|1|Web
  Naga, Shinomen, Greensnake|11|Humanoid|Medium|1|Oriental Adventures

.. code-block:: bash

  sqlite> select distinct dnd_template.name, dnd_rulebook.name, page from dnd_template inner join template_type on dnd_template.id=template_id inner join dnd_monstertype on dnd_monstertype.id=output_type inner join (select id as input_id, name as input_name from dnd_monstertype) on input_id=base_type inner join dnd_rulebook on rulebook_id=dnd_rulebook.id where (dnd_monstertype.name="Undead" or dnd_monstertype.name="Plant" or dnd_monstertype.name="Dragon" or (dnd_monstertype.name="Elemental" and input_name!="Elemental") ) and input_name!="Undead" and input_name!="Plant" and input_name!="Dragon" and input_name!="Animal" order by dnd_rulebook.name;
  Bone Naga|Serpent Kingdoms|73 http://archive.wizards.com/default.asp?x=dnd/ex/20040709a&page=4
   A bone naga is a skeletal undead creature created from a naga by a spellcaster (usually of its own race). A create undead spell can produce a bone naga from any naga subject with fewer Hit Dice than the creator.
   Though it despises servitude, a bone naga unswervingly obeys its creator, attacking even other nagas if so commanded. Should its master die, the bone naga becomes free-willed and can choose its own destiny.
   "Bone naga" is an acquired template that can be added to any naga (referred to hereafter as the base creature). Including, say, a greensnake.
   Abilities: As an undead creature, a bone naga has no Constitution score.
   Challenge Rating: Same as the base creature +1.
   Treasure: None
   Alignment: Any evil.
   Telepathy (Su): A bone naga can communicate telepathically with any creature within 250 feet that has a language.
  Bonesinger|Ghostwalk|158
  Tainted Minion|Heroes of Horror|153
  Mummified Creature|Libris Mortis: The Book of the Dead|110
  Necromental|Libris Mortis: The Book of the Dead|112
  Half-Dragon|Monster Manual v.3.5|146

Bonesinger is a template that can be applied to any creature that has at least one level as a bard
Cooperative Magic (Sp): A bonesinger can use a standard action to increase by 2 the save DC of a spell cast by an adjacent bonesinger. The bonesinger must ready an action to help in this manner; the trigger is the other bonesinger beginning to cast a spell.

No template turns a non-elemental into an elemental, so the choices for a necromental are...limited.

Tainted minion is an acquired template that can be added to any humanoid or monstrous humanoid creature with at least mild levels of both corruption and depravity (referred to hereafter as the base creature).
 A character who spends the night in a haunted location must make a DC 20 Will save or have his depravity score increase by 1.
 It is most often applied to a creature that dies because its corruption score exceeds the maximum for severe corruption for a creature with its Constitution score
Fear Aura (Su): Tainted minions are shrouded in a constant aura of terror and evil. Creatures within a 30-foot radius of a tainted minion must succeed on a Will save (DC 10 + 1/2 the tainted minion's level + its Cha modifier) or become shaken. (No duration specified...but it's fear, so presumably for the rest of the encounter.)
 http://www.d20srd.org/srd/specialAbilities.htm#fearAura
 The use of this ability is a free action.
 But since the tainted minion's aura is specifically *constant*, they cannot suppress it (though the source of the supernatural fear might not be obvious).
Change Shape (Su): A tainted minion can assume the form of any humanoid creature. See page 306 of the Monster Manual for details. Note that a tainted minion loses no Intelligence and can speak normally.
Abilities: Increase from the base creature as follows: Str +4, Dex +2, Cha +4. As an undead creature, a tainted minion has no Constitution score.
Taint: A tainted minion no longer acquires taint. For purposes of special abilities, its corruption and depravity scores are both considered to be equal to half its Charisma score +1.

Sites strongly associated with the undead and with death often bestow corruption.
For every 24 hours spent in a tainted place, a character must make another saving throw to avoid her appropriate taint score increasing by 1. The base DC is 10, +5 for every consecutive 24 hours of exposure.
Any creature that dies in a tainted area animates in 1d4 hours as an undead creature, usually a zombie of the appropriate size. Burning a corpse protects it from this effect.
Anyone who casts or is subject to a spell with the evil descriptor while within 50 feet of a clump of abyssal blackgrass must make a successful Fortitude save (DC 10 + spell level) or increase his corruption score by 1.
As it turns out, a 1st-level Healer is terrifyingly effective at using abyssal blackgrass to increase multiple people's taint scores at once.
Of course, a Healer cannot command undead.

.. code-block:: bash

  sqlite> select distinct dnd_characterclass.name, target, area, range, duration, dnd_spell.name from dnd_spell inner join dnd_spellclasslevel on dnd_spell.id=dnd_spellclasslevel.spell_id inner join dnd_characterclass on character_class_id=dnd_characterclass.id inner join dnd_spell_descriptors on dnd_spell_descriptors.spell_id=dnd_spell.id inner join dnd_spelldescriptor on spelldescriptor_id=dnd_spelldescriptor.id where dnd_spelldescriptor.name like "%Evil%" and level=0;
  Wizard|One living creature with a tongue||Close (25 ft. + 5 ft./2 levels)|1 round|Slash Tongue
  Cleric|One living creature with a tongue||Close (25 ft. + 5 ft./2 levels)|1 round|Slash Tongue
  Healer||Cone-shaped emanation|30 ft.|10 min./level|Deathwatch

Touch of Taint (Ex): Anyone struck by a taint elemental, or who physically touches a taint elemental, must succeed on a Fortitude save or gain corruption points.
A necromental taint elemental could have the Touch of Taint [Monstrous] feat to bestow depravity. Of course, even a small taint elemental has 2HD.

It takes 42 corruption to kill a Con9--12 creature. More generally, 14*ceil(Con/4).
If a character's corruption score ever exceeds the severe taint threshold, she dies, and 1d6 hours later she rises as a tainted minion --- a hideous, evil creature under the control of the DM.

Libris Mortis: "Mummified creature is an acquired template that can be added to any corporeal giant, humanoid, or monstrous humanoid."
Savage Species: "Mummified is an acquired template that can be added to any corporeal animal, giant, or humanoid." Libris Mortis is the more up-to-date source; Libris Mortis talks about Damage Reduction 5/-, while Savage Species talks about Damage Reduction 5/+1 and half damage, 3.0 terminology.
A mummified creature speaks all the languages it spoke in life
Speed: A mummified creature's land speed decreases by 10 feet (to a minimum of 10 feet). The speeds for other movement modes are unchanged.
Abilities: A mummified creature's ability scores are modified as follows: Str +8, Int -4 (minimum 1), Wis +4, Cha +4. As an undead creature, a mummified creature has no Constitution score.
The process of becoming a mummy is usually involuntary, but expressing the wish to become a mummy to the proper priests (and paying the proper fees) can convince them to bring you back to life as a mummy. The mummy retains all class abilities it had in life, provided that its new ability scores still allow it to use them (a wizard loses access to some spell levels, for instance). A loss of Intelligence does not retroactively remove skill points from a mummified creature.
Special Qualities: A mummified creature gains the special qualities described below...which do not include turn resistance.

Can you get either a tainted minion or a mummified creature of less than one Hit Die, thus giving you an intelligent undead minion of less than one Hit Die? Why, it's our old friend the Muckdweller!

.. code-block:: bash

  sqlite> select distinct dnd_monster.name, intelligence, dnd_monstertype.name, constitution, land_speed, dnd_racesize.name, hit_dice, dnd_rulebook.name from dnd_monster inner join dnd_monstertype on dnd_monstertype.id=dnd_monster.type_id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstertype.name="Humanoid" or dnd_monstertype.name="Monstrous Humanoid" or dnd_monstertype.name="Giant") and hit_dice<1 order by hit_dice, dnd_monstertype.name;
  Muckdweller|10|Monstrous Humanoid|10|20|Tiny|-4|Serpent Kingdoms

Alternatively, is there another template that can make unsuitable monsters suitable for tainted minion or mummified creature?

.. code-block:: bash

  sqlite> select distinct dnd_template.name, dnd_rulebook.name, page from dnd_template inner join template_type on dnd_template.id=template_id inner join dnd_monstertype on dnd_monstertype.id=output_type inner join (select id as input_id, name as input_name from dnd_monstertype) on input_id=base_type inner join dnd_rulebook on rulebook_id=dnd_rulebook.id where (dnd_monstertype.name="Humanoid" or dnd_monstertype.name="Monstrous Humanoid" or  (dnd_monstertype.name="Giant" and input_name!="Giant") ) and input_name!="Humanoid" and input_name!="Monstrous Humanoid" order by dnd_rulebook.name;
  Half-Troll|Fiend Folio|92
  Tauric Creature|Monster Manual II|216
  Incarnate Construct|Savage Species|120

The Incarnate Construct spell is hard to come by.
A tauric creature's type changes to monstrous humanoid. The template can be added to any Small or Medium-size corporeal humanoid (referred to hereafter as the base humanoid) and any Medium-size or Large corporeal animal, beast, or vermin with at least four legs (referred to hereafter as the base creature). Of course, you have to start with a humanoid, since this would be just if you wanted to mix in an animal or vermin. There are better ways to get animals to serve you, and most vermin abilities are Constitution-based.

Half-troll is an inherited template that can be added to any animal, dragon, fey, giant, humanoid, magical beast, monstrous humanoid, or outsider (referred to hereafter as the base creature). The creature's type becomes giant.
Fast Healing (Ex): A half-troll heals 5 points of damage each round so long as it has at least 1 hit point. A mummified half-troll does not lose this special quality.
Abilities: Adjust from the base creature as follows: Str +6, Dex +2, Con +6, Int -2, Cha -2.
Alignment: Usually chaotic neutral or chaotic evil.
If you can't rebuke dragons, you can cross-breed a puppeteer with a dragon (preferably one immune to fire or acid), then cross-breed the result with a troll, then mummify the grandchild, then rebuke and command the mummified half-troll quarter-dragon puppeteer.


You know, Imcarnate Construct makes me wonder. What templates can convert a non-living creature into a living creature?

.. code-block:: bash

  sqlite> select distinct dnd_template.name, dnd_rulebook.name, page from dnd_template inner join template_type on dnd_template.id=template_id inner join dnd_monstertype as output on output.id=output_type inner join dnd_monstertype as input on input.id=base_type inner join dnd_rulebook on rulebook_id=dnd_rulebook.id where output.name!="Construct" and output.name!="Undead" and (input.name="Construct" or input.name="Undead") order by dnd_rulebook.name;
  Corrupted Creature|Book of Vile Darkness|186
  Corrupted by the Abyss|Expedition to the Demonweb Pits|190
  Pseudonatural Creature|Lords of Madness|161
  Pseudonatural Creature|Manual of the Planes|212
  Pseudonatural Creature|Complete Arcane|160
  Pseudonatural Creature|Epic Level Handbook|212
  Worm That Walks|Epic Level Handbook|228
  Half-Elemental|Manual of the Planes|188
  Half-Elemental|Return to the Temple of Elemental Evil|160
  Half-Illithid|Underdark|89
  Incarnate Construct|Savage Species|120

There are a couple of ways, most connected to the Abyss or the Far Realm, which makes sense.
Kaortis, however, can only apply the pseudonatural template to living creatures.

Half-elemental is a template that can be added to any corporeal creature with an Intelligence score of 4 or more. Because the half-elemental is still mostly flesh, it cannot be of the elemental type. Instead, the creature's type changes to outsider.
Much rarer than half-celestials or fiends, half-elementals are the result of unions between elementals and mortal creatures or are created by some magical infusion of elemental power into a mortal at birth (usually through strange and often distasteful rites). Such creatures are normally left among their mortal kin, never again thought of by their otherworldly sires.
There's probably a limited-lifespan undead or construct somewhere. (Though they might not be "mortal", as they're still immune to death effects...) So a half-elemental undead could probably be created via strange and often distasteful rites, but we don't know what those rites might be.

Half-illithids are the progeny of mind flayers and various other creatures. Most often, such progeny are formed through magical tampering with the reproductive process of the host creature, rather than through direct mating.
Half-illithid is an inherited template that can be added to any corporeal creature that is not a construct.

Corrupted by the Abyss is an inherited or acquired template that can be added to any corporeal creature. The creature's type changes to aberration.
Creatures corrupted by the Abyss are sometimes native to the Infinite Layers of the Abyss. In most cases, however, they originate on other planes but become tainted by the Abyss through long-term residence there.


Half-dragon is an inherited template that can be added to any living, corporeal creature.
Abilities: Increase from the base creature as follows: Str +8, Con +2, Int +2, Cha +2.

.. code-block:: bash

  sqlite> select distinct dnd_monster.name, intelligence, dnd_monstertype.name, land_speed, dnd_racesize.name, hit_dice, dnd_rulebook.name from dnd_monster inner join dnd_monstertype on dnd_monstertype.id=dnd_monster.type_id inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on dnd_rulebook.id=rulebook_id where (dnd_monstertype.name!="Construct" and dnd_monstertype.name!="Undead") and intelligence is not null and hit_dice<-2 order by hit_dice, dnd_monstertype.name;
  Moonrat|2|Magical Beast|15|Tiny|-4|Monster Manual II
  Puppeteer|14|Magical Beast|5|Fine|-4|Expanded Psionics Handbook
  Muckdweller|10|Monstrous Humanoid|20|Tiny|-4|Serpent Kingdoms

Under the influence of lunar light, moonrats also gain the ability to organize, converse with one another, formulate complex plans, and operate complicated devices.
Protip: make it a male puppeteer and a female dragon. The reverse will not end well.

Disappointments:
Turn Resistance (Ex): A huecuva is treated as an undead with 2 more Hit Dice than it actually has for the purposes of turn, rebuke, command, or bolster attempts.
Turn Resistance (Ex): A juju zombie has turn resistance +4.
Turn Resistance (Ex): A greater mummy has +4 turn resistance.
Turn Resistance (Ex): A swordwraith is treated as an undead with 2 more Hit Dice than it actually has for the purposes of turn, rebuke, command, or bolster attempts.
Turn Resistance (Ex): A mumia has turn resistance +2.
Turn Resistance (Ex): An umbral creature gains +2 turn resistance.
Turn Resistance (Ex): A necropolitan has +2 turn resistance.
Turn Resistance (Ex): A ghost brute has +2 turn resistance.
Turn Resistance (Ex): A gravetouched ghoul has +2 turn resistance.
Turn Resistance (Ex): A ghost has +4 turn resistance.
Web Mummy: The base creature's Hit Dice increase by 3.
Deadened Mind (Ex): A yellow musk zombie recalls nothing of its previous life, and it exists only to serve its parent plant. It cannot make use of class abilities, skills, or feats it previously knew. It also cannot use magic devices, although it can still wield weapons and use armor. Intelligence of 2







All half-fey have butterflylike wings unless the base creature has wings already.
That would seem to restrict what fey can sire half-fey.
sqlite> select dnd_racesize.name, dnd_monster.name,speed,dnd_rulebook.name from dnd_monster inner join dnd_monstertype on type_id=dnd_monstertype.id and dnd_monstertype.name="Fey" inner join monster_movement_mode on dnd_monster.id=monster_id and (abbrev='f') inner join dnd_racesize on size_id=dnd_racesize.id inner join dnd_rulebook on rulebook_id=dnd_rulebook.id order by speed;
http://archive.wizards.com/default.asp?x=dnd/fey/20031121a
Forestfolk are born with a thin, wet membrane attached to their underarms and torso. As they grow from infancy to childhood, this membrane dries and lengthens, eventually allowing them to glide through the air for short periods of time.
Forestfolk are not true flyers. A forestfolk always must dive at least 10 feet when using a move action to fly.
Joystealers do not have wings.
An usunag is a cloud of gas. http://archive.wizards.com/default.asp?x=dnd/psb/20070711a&page=4
Storm riders do not have wings. http://archive.wizards.com/default.asp?x=dnd/fey/20040110a
Grigs have cricket wings, which is close enough. Pixies have gossamer wings.
Ruin chanters do not have wings.
Hoarfrosters are incorporeal.
http://archive.wizards.com/default.asp?x=dnd/fey/20040718a
Sleeping blossom sprites tend to have pale skin, with red- or orange-tinted wings.
Diminutive Fey (Swarm)
Abilities: Str 4, Dex 17, Con 10, Int 8, Wis 9, Cha 21
An individual shimmerling looks like a 4-inch tall elf with dragonfly wings.
Dreamfanes are incorporeal.
Petals have petallike wings.
A frostwind virago does not have wings.
Shaedlings have fine wings like those of a dragonfly.
A gloura has gray mothlike wings.
Rime sprites look like animated ice statues of beautiful or handsome elves with snow for hair. That sounds like they don't have wings. http://archive.wizards.com/default.asp?x=dnd/fw/20030223a
Rimefire eidolons do not have wings.
http://archive.wizards.com/default.asp?x=dnd/fw/20020817a
A siabrie's wings are glimmering and crystalline, like stained glass. Close enough.

It took some trawling through false positives, but now we probably have a complete list of possible fey parents: Tiny grig, Small pixie, Diminutive sleeping blossom sprite, Fine shimmerling, Tiny petal, Medium shaedling, Medium gloura, or Medium siabrie.
The child's fly speed might be faster than the parent's because of hybrid vigor. (You could even justify using a Small forestfolk, if it's more thematically appropriate.) Or just because the child is quite likely to be physically larger. In the event you find yourself stuck with a Tiny female fey, the use of a proxy mother is strongly recommended.



On a lighter note, I always thought that a "living will" sounded like a magical incorporeal construct. Say, are there any incorporeal constructs?

.. code-block:: bash

  sqlite> select distinct challenge_rating, dnd_monster.name, dnd_rulebook.name from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join monster_has_subtype on dnd_monster.id=monster_has_subtype.monster_id inner join dnd_monstersubtype on monster_has_subtype.subtype_id=dnd_monstersubtype.id inner join dnd_rulebook on rulebook_id=dnd_rulebook.id where (dnd_monstertype.name="Construct") and (dnd_monstersubtype.name="Incorporeal") order by challenge_rating;
  3|Umbral Spy|The Forge of War
  18|Golem, Prismatic|Monster Manual III




