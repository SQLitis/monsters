
.. role:: bash(code)
   :language: bash


monsters.py merges XLS and SQLite data to make a searchable database.
All the data comes from other people; this is an automatic script rather than a one-shot conversion so that any later updates won't need my involvement to re-run the conversion.

Type :bash:`python monsters.py --help` for instructions on how to run the conversion.

Here we are more concerned with what you can do after successfully running the conversion.

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

`Brain in a Jar <http://archive.wizards.com/default.asp?x=dnd/iw/20041015b&page=2>`_
`Time Wight <http://archive.wizards.com/default.asp?x=dnd/mm/20030620a>`_




.. code-block:: bash

  sqlite> select dnd_monster.name,dnd_special_ability.name from dnd_monster inner join dnd_monstertype on dnd_monster.type_id=dnd_monstertype.id inner join monster_special_ability on dnd_monster.id=monster_id inner join dnd_special_ability on dnd_special_ability.id=special_ability_id where (dnd_special_ability.name like "%rebuke%" or dnd_special_ability.name like "%control%" or dnd_special_ability.name like "%command%");
  Earth Whisper|control earth creatures

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








