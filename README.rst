
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


-------------
Version notes
-------------
The biggest problem right now is the lack of rulebook data.
Obviously you can run to the `Monster Finder <http://monsterfinder.dndrunde.de/>`_ once you've selected a monster (an excellent tool, though very limited in the sorts of searches it can run). But it would be better to have that information directly available from the database, especially since the Monster Finder only includes 1322 out of 4447 monsters.

Some of the rulebook data will be obtained by cannibalizing `Hey I Can Chan's list <https://rpg.stackexchange.com/questions/1138/how-do-you-tell-if-a-dd-book-is-3-0-or-3-5>`_ or more accurately `Jackinthegreen's revision <http://www.minmaxboards.com/index.php?topic=15375.0>`_, but not all of them are included.

.. code-block:: bash

  CREATE TABLE "dnd_rulebook" (
  "dnd_edition_id" int(11) NOT NULL,
  "name" varchar(128) NOT NULL,
  "abbr" varchar(7) NOT NULL,
  "official_url" varchar(255) NOT NULL,
  "slug" varchar(128) NOT NULL,
  "published" date NOT NULL,

.. code-block:: python

 rulebook_abbreviations = {'MM1':'Monster Manual',
 'DotU':'Drow of the Underdark',
 'Planar':'Planar Handbook',
 'ToHS':'Towers of High Sorcery',
 'CotSQ':'City of the Spider Queen',
 'Aldriv':"Aldriv's Revenge",
 'Exp':'Expedition to the Demonweb Pits',
 'Dunge':'Dungeonscape',
 'Psi':'Psionics Handbook (Web Enhancement)',
 'SoS':'Spectre of Sorrows',
 'CoV':'Champions of Valor',
 'Loona':'Loona, Port of Intrigue',
 'ToH':'Tomb of Horror',
 'MM2':'Monster Manual 2',
 'MM3':'Monster Manual 3',
 'MM4':'Monster Manual 4',
 'MM5':'Monster Manual 5',
 'FF':'Fiend Folio',
 'ElderE':'Elder Evils',
 'RoS':'Races of Stone',
 'ELH':'Epic Level Handbook',
 'PoC':'Price of Courage', 'WD':'City of Splendors: Waterdeep', 'MT':"Midnight's Terror", 'RTF':'Return to the Temple of the Frog',
 'RotW':'Races of the Wild', 'ECS':'Eberron Campaign Setting', 'ExUn':'Expedition to Undermountain', 'SotAC':'Secrets of the Alubelok Coast', 'Sheep':"Sheep's Clothing",
 'A&E':'Arms & Equipment Guide', 'SvgSp':'Savage Species (Web Enhancement)', "Xen'd":"Secrets of Xen'drik", 'LEoF':'Lost Empires of Faerun', 'Kruk':'The Lost Tomb of Kruk-Ma-Kali', 'SD':'Stone Dead',
 'BoED':'Book of Exalted Deeds', 'FC1':'Fiendish Codex 1', 'Storm':'Stormwrack', 'FoW':'The Forge of War',
 'SoCo':"Something's Cooking",
 'Draco':'Draconomicon',
 'MH':'Miniatures Handbook',
 'BoKR':'Bestiary of Krynn', 'MgoF':'Magic of Faerun', 'RoF':'Races of Faerun', 'DoK':'Dragons of Krynn', 'MoF':'Monsters of Faerun',
 'GotP':'Garden of the Plantmaster',
 'StSt':'The Standing Stone', 'BoBS':'Bastion of Broken Souls',
 'DrC':'Dragon Compendium', 'MoI':'Magic of Incarnum',
 'HoD':'Harvest of Darkness', 'EnvIm':'Environmental Impact',
 'DDen':"Dangerous Denizens - The Monsters of Tellene",
 }
 #EPH	Expanded Psionics Handbook	Sand	Sandstorm	Sarlo	Secrets of Sarlona	ItDL	Into the Dragon's Lair	SaD	Stand and Deliver	DS	Desert Sands
 #BoVD	Book of Vile Darkness	FC2	Fiendish Codex 2	ToB	Tome of Battle	FN	Five Nations	Serp	Serpent Kingdoms	Forge	The Forge of Fury	FoN	Force of Nature
 #City	Cityscape	Frost	Frostburn	ToM	Tome of Magic	MoE	Magic of Eberron	ShSo	Shining South	WndW	The Secret of the Windswept Wall	GW	Ghostwalk
 #C.Ar	Complete Arcane	HoB	Heroes of Battle	DCS	Dragonlance Campaign Setting	Sharn	Sharn - City of Towers	UE	Unapproachable East	RTEE	Return to the Temple of Elemental Evil	OA	Oriental Adventures
 #C.Psi	Complete Psionic	HoH	Heroes of Horror	AoM	Age of Mortals	CoR	Champions of Ruin	Under	Underdark	TVoS	The Vessel of Stars	###	Dragon Magazine
 #C.War	Complete Warrior	LM	Libris Mortis	KoD	Key of Destiny	F&P	Faiths and Pantheons, SlvSk	The Silver Skeleton	A##	Dragon Magazine Annual 00/01
 #Deities	Deities and Demigods	LoM	Lords of Madness	BoKR	Bestiary of Krynn Revised	FRCS	Forgotten Realms Campaign Setting	BaS	Blood and Shadows - The Dark Elves of Tellene	LDR	Lest Darkness Rise	Web	Web content
 #DrM	Dragon Magic	MotP	Manual of the Planes	HOS	Holy Order of the Stars	SM	Silver Marches	LoMys	Lands of Mystery	ToBV	The Treasure of the Black Veils	108 total sources
 # if the abbreviation is just a number then it's a Dragon magazine number



As a temporary hack, highmage's database is vendored in for psionic power data.


------------------
Using the database
------------------

Perhaps you've heard from Monsieur Meuble that humans and halflings are the only creatures in all of creation that cannot see in the dark.
We can check whether there are any creatures besides humans and halflings that have neither darkvision nor low-light vision.
We can immediately note that all types besides Humanoid give one of those automatically (yeah, yeah, except Ooze, that's a special case since they're all *blind*).

.. code-block:: bash

  sqlite> select dnd_monster.name from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id where dnd_monstertype.name="Humanoid" and not exists (select 1 from monster_special_ability inner join dnd_special_ability on monster_special_ability.special_ability_id=dnd_special_ability.id and monster_special_ability.monster_id=dnd_monster.id and (dnd_special_ability.name like "%darkvision%" or dnd_special_ability.name like "%low-light vision%") );




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

  sqlite> select distinct dnd_monster.name,hit_dice from dnd_monster inner join monster_subtype on dnd_monster.id=monster_subtype.monster_id inner join dnd_monstersubtype on monster_subtype.subtype_id=dnd_monstersubtype.id where (dnd_monstersubtype.name="Earth") and hit_dice<=2 order by hit_dice;
  Gen, Earth|1
  Elemental, Earth, Small|2
  Paraelemental, Magma, Small|2
  Paraelemental, Ooze, Small|2
  Stonechild|2
  Gargoyle, Urban|2

Earth whispers can advance in hit dice, or can be granted bonus hit dice by a bard. If we allow the hit dice to go a little higher, what spell-like abilities show up?

.. code-block:: bash

  sqlite> select distinct dnd_spellclasslevel.level,dnd_spell.name,dnd_monster.name,hit_dice from monster_spell_like_ability inner join dnd_monster on monster_spell_like_ability.monster_id=dnd_monster.id inner join dnd_spell on dnd_spell.id=monster_spell_like_ability.spell_id inner join dnd_spellclasslevel on dnd_spell.id=dnd_spellclasslevel.spell_id inner join monster_subtype on dnd_monster.id=monster_subtype.monster_id inner join dnd_monstersubtype on monster_subtype.subtype_id=dnd_monstersubtype.id where (dnd_monstersubtype.name="Earth") and hit_dice<=3 order by hit_dice,dnd_spellclasslevel.level;
  2|Soften Earth and Stone|Mephit, Earth|3
  2|Glitterdust|Mephit, Salt|3
  3|Stinking Cloud|Mephit, Sulfur|3








