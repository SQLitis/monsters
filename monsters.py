#!/usr/bin/env python
"""
Usage: python monsters.py

# Sources:
# ezkajii's Monster Compendium.xls for most of the monster data
# highmage's dnd35.db for psionic powers
# dndtools' dnd.sqlite for most of the spell data

# CreatureInfo.csv from HeroForge on GitHub has many fewer monsters, does not have eg tirbana, probably not worth it
"""

from __future__ import print_function
import os,sys,os.path
import shutil
import itertools
import argparse
#os.chdir('xlrd-1.0.0')
sys.path.append(os.path.join(os.getcwd(), 'xlrd-1.0.0') )
#print(sys.path)
import re
import datetime
import sqlite3
import csv
import xlrd # https://github.com/python-excel/xlrd
# https://www.blog.pythonlibrary.org/2014/04/30/reading-excel-spreadsheets-with-python-and-xlrd/
#import ipdb
import cProfile,pstats

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


def fraction_to_negative(string):
  """All fractions of Hit Dice etc happen to be of the form 1/#,
  so they can be encoded as negative integers.
  """
  #print('fraction_to_negative', string, type(string) )
  try:
    return int(string)
  except ValueError as E:
    if string[:2] == '1/':
      return -int(string[2:])
    #elif string == '-': return None
    else:
      raise

def integer_or_non(string):
  if string == '-': return None
  else: return int(string)

goodEvilToInt = {'G':1, 'E':-1, 'N':0, 'X':0}
lawChaosToInt = {'L':1, 'C':-1, 'N':0, 'X':0}
# X really means any, like angels are any good, maybe really I should have an intersection table of monster_ids and alignments

spellNameErrors = {'resistance to energy':'Resist Energy', # Angel, Solar
  'protection from flame':'Protection from Energy (fire only)',
  'mass enlarge':'Mass Enlarge Person', # Greater Barghest
  # from 3.5 update booklet:
  'enlarge':'Enlarge Person',
  'reduce':'Reduce Person',
  'charm person or animal':'Charm Animal',
  'change self':'Disguise Self',
  'mass charm':'Charm Monster, Mass',
  'circle of doom':'Inflict Light Wounds, Mass',
  'mass haste':'Haste',
  'create/destroy water':'Create Water', # not really an error, but easier to handle blue dragon this way
  'summon djinni':'Summon Monster VII (djinni only)',
  'colossal vermin':'Giant Vermin (can increase from Large to Gargantuan and from Huge to Colossal)',
  'permanent creation (food for 2d12 people, 52 cu.ft. of soft goods, or 18 cu.ft. of wooden items; or 400bls of metal items at 10 times the duration of such items produced by major creation)':'Major Creation',
  'transmute rock to mud / mud to rock':'transmute rock to mud (or mud to rock)', # not really an error, but easier to handle copper dragon this way
  'transmute rock to lave':'transmute rock to lava',
  'yare of air':'yari of air',
  'protection from chaos/evil/good/law':'protection from evil', # not really an error, but easier to handle Grimweird
  'power word (any)':'Power Word Petrify', # sqlite> select distinct level,dnd_spell.name from dnd_spell inner join dnd_spellclasslevel on dnd_spell.id=dnd_spellclasslevel.spell_id inner join dnd_characterclass on character_class_id=dnd_characterclass.id where dnd_spell.name like "power word%" order by level;
  'symbol (any)':'Symbol of Weakness', # sqlite> select distinct level,dnd_spell.name from dnd_spell inner join dnd_spellclasslevel on dnd_spell.id=dnd_spellclasslevel.spell_id inner join dnd_characterclass on character_class_id=dnd_characterclass.id where dnd_spell.name like "symbol%" order by level;
  'locate person':'Locate Creature',
  'turn wood':'Repel Wood',
  'slow poison':'Delay Poison',
  'great sh9out':'Great Shout',
  'wood shape)':'Wood Shape',
  'invisibility\\':'invisibility',
  'se invisibility':'see invisibility',
  'domination':"Psionic Dominate",
  'mind rap (5 rds*)':"Mind Trap (5rounds)",
  'psychic thrust (6d6*)':"Psychic Crush (6d6*)", # http://www.d20srd.org/srd/psionic/monsters/neothelid.htm
  'painful touch':"Painful Strike",
  'blindness':'Blindness/Deafness (blindness only)',
  'remove blindness':'Remove Blindness/Deafness (blindness only)',
  'create grater undead':'Create Greater Undead',
  'animated dead':'Animate Dead',
  'discern lie':'Discern Lies',
  'ghost sounds':'Ghost Sound',
  'chain lighting (dmg increased as though empowered)':'Chain Lightning (Empowered)',
  'call lighting':'Call Lightning',
  'call lighting storm':'Call Lightning Storm',
  "Snilloc's snowball storm":"Snilloc's Snowball Swarm",
  "word of law":"Dictum",
  'purify food or drink':'Purify Food and Drink',
  'create food and drink':'Create Food and Water',
  'pyrotechnic':'Pyrotechnics',
  'firestorm':'Fire Storm',
  'brainlock (any nonmindless*)':'Brain Lock (any nonmindless*)',
  'stonetell':'Stone Tell',
  'cloud kill':'Cloudkill',
  'acid cloud':'Acid Fog',
  'cloud of fish':'Fish Cloud',
  'flaming shroud':'Shroud of Flame',
  'mind store':'Mind Seed',
  'far punch':'Far Hand',
  'combat prescience':'Prescience, Offensive',
  'shield of prudence':'Thought Shield', # Shield of Prudence is NOT Thought Shield, Hamaguan has both http://archive.wizards.com/default.asp?x=dnd/psb/20030523c
  'concussive detonation (9d6*)':'Concussion Blast (9d6*)', # NOT, Hammerfish has both 
  'vigilance':'Vigilant Slumber',
  'dowsing':'Locate Water',

  'chameleon power':"Chameleon",
  'endurance':"Bear's Endurance",
  "Nystul's undetectable aura":"Nystul's Magic Aura",
  'wave of fire':'Wall of Fire',
  'cause disease':'Contagion',
  'cloud trapeze (self +50lbs only)':'Wind Walk (self +50lbs only)',
  'half undead':'Halt Undead',
  'door':'Doom', # http://www.enworld.org/forum/showthread.php?491761-Frostburn-Frost-Giant-Spiritspeaker-s-spell-like-ability
  'crown of brilliant':'Crown of Brilliance',
  'deep  slumber':'Deep Slumber',
                  }
typeNameErrors = {'Exraplanar':'Extraplanar', 'Extraplanr':'Extraplanar','Extaplanar':'Extraplanar'}
def fix_subtype(subtype):
  subtype = subtype.strip()
  if subtype in typeNameErrors:
    subtype = typeNameErrors[subtype]
  return subtype

def spell_name_to_id(curs, spellName):
  curs.execute('''SELECT published,dnd_spell.id from dnd_spell INNER JOIN dnd_rulebook on dnd_spell.rulebook_id=dnd_rulebook.id WHERE dnd_spell.name like ? ORDER BY published;''', (spellName,) )
  results = curs.fetchall()
  #print('spell_name_to_id', spellName, results)
  if len(results) == 0:
    words = spellName.split()
    if words[0].lower() in ('lesser', 'greater', 'mass', 'psionic'):
      return spell_name_to_id(curs, ' '.join(words[1:]) + ', ' + words[0])
    else:
      raise KeyError(spellName + " not found in spell database")
  spell_id = results[-1][1]
  assert spell_id is not None
  return spell_id




darkvisionRE = re.compile(r"DV\d{2,3}")
damageReductionRE = re.compile(r"DR \d{1,2}/[\w\s\-]+")
spellResistanceRE = re.compile(r"SR \d{1,2}")

casterLevelValueREstring = '(?:(?:\d{1,2})|(?:HD)|(?:lvl))\s*(?:\([\w\s]+\d?\))?'
casterLevelTagREstring = '(?:C|M|T)L=?\s?'
casterLevelREstring = casterLevelTagREstring + '(' + casterLevelValueREstring + ')'
casterLevelREstringNoncapturing = casterLevelTagREstring + '(?:' + casterLevelValueREstring + ')'
casterLevelRE = re.compile(casterLevelREstring)
matchObj = casterLevelRE.match('CL12')
assert matchObj is not None
assert matchObj.group(0) == 'CL12'
assert matchObj.group(1) == '12' # keep these, if fiddle with caster level tag RE sometimes the | catches everything to the right or somesuch
matchObj = casterLevelRE.match('CLHD (min3)')
assert matchObj is not None
assert matchObj.group(0) == 'CLHD (min3)'
matchObj = casterLevelRE.match('CL10 (with Graystaff only), at will')
assert matchObj is not None
if matchObj.group(0) != 'CL10 (with Graystaff only)':
  raise RuntimeError(matchObj.group(0) )
#if matchObj.group(1) != '10': # 10 (with Graystaff only) dunno if that's okay
#  raise RuntimeError(matchObj.group(1) )

parentheticalREstring = r'\([^)]*\)' # ( followed by any characters other than ), then )
parentheticalREstringWithGroup = r'\(([^)]*)\)' # for some unknown reason, including the group in the main causes noUnparenthesizedCommasRE to only match the interiors of parentheses
parentheticalRE = re.compile(parentheticalREstringWithGroup)
singleCharOrParenthesizedREstring = '[^,(]|' + parentheticalREstring
noUnparenthesizedCommasRE = re.compile('(?:' + singleCharOrParenthesizedREstring + ')+')
frequencyREstring = r"((?:A|at will(?: as a \w+ action:)?(?:\s*\(every \drds\))?)|(?:\d/day)|(?:\d/hour)|(?:\d/week)|(?:\d/tenday)|(?:\d/month)|(?:\d/year)|(?:\d/century))"
freqChangeRE = re.compile(r'(?:;|,|^)?(?:In addition,)?(?:continually active,)?\s*(?:(' + casterLevelREstringNoncapturing + "),)?\s*" + frequencyREstring + '\s*-\s*')
# planetar: CL17, at will-continual flame, dispel magic, holy smite, invisibility (self only), lesser restoration, remove curse, remove disease, remove fear, speak with dead, 3/day - blade barrier, flame strike, power word stun, raise dead, waves of fatigue; 1/day - earthquake, greater restoration, mass charm monster, waves of exhaustion. 
# emerald dragon: at will - object reading 3/day - greater invisibility
# Bheur: CL10 (with Graystaff only), at will - hold person, solid fog; 3/day - cone of cold, ice storm, wall of ice; CL10 (not Graystaff dependent), at will - chill metal, ray of frost, Snilloc's snowball storm; 1/tenday - control weather
matchObj = freqChangeRE.match("CL10 (with Graystaff only), at will - hold person; CL10 (not Graystaff dependent), at will - chill metal")
assert matchObj is not None
freqChangeRE.split("CL10 (with Graystaff only), at will - hold person; CL10 (not Graystaff dependent), at will - chill metal")

eightByteIntMax = 9223372036854775807 # max can store in 
assert eightByteIntMax + 1 == 2**63

def parse_comma_separated_spells(commaSeparatedSpells):
  # comma errors:
  commaSeparatedSpells = commaSeparatedSpells.replace('faerie, fire', 'faerie fire').replace('greater teleport, (self', 'greater teleport (self').replace('confusion dimension door', 'confusion, dimension door').replace('aura sight (chaos/law only) (', 'aura sight (chaos/law only, ').replace('energy arc (fire only) (', 'energy arc (fire only, ').replace('energy missile (fire only) (', 'energy missile (fire only, ').replace('energy burst (fire only) (', 'energy burst (fire only, ').replace('energy ray (electricity only) (', 'energy ray (electricity only, ').replace('energy stun (sonic only) (', 'energy stun (sonic only, ').replace('psionic daze (affects any creature type) (', 'psionic daze (affects any creature type, ')
  # Obsidian Dragon has all the energy blah powers http://archive.wizards.com/default.asp?x=dnd/psb/20030124b
  #  it really is Flaming Shroud, I dunno
  spells = [spell.strip() for spell in noUnparenthesizedCommasRE.findall(commaSeparatedSpells)]
  ret = list()
  for spell in spells:
          if spell in spellNameErrors: spell = spellNameErrors[spell]
          matchObj = parentheticalRE.search(spell)
          if matchObj is not None:
            if matchObj.end() != len(spell): raise RuntimeError(spell)
            assert spell[matchObj.start() - 1] == ' '
            parenthetical = matchObj.group(1)
            spell = spell[:matchObj.start()-1]
          else:
            parenthetical = None
          words = spell.split()
          if words[0].lower() in ('quickened', 'heightened', 'maximized', 'empowered', 'violated', 'mortalbane', 'corrupted'):
            if parenthetical is None: parenthetical = words[0]
            else: parenthetical = words[0] + ', ' + parenthetical
            spell = ' '.join(words[1:])
          ret.append( (spell, parenthetical) )
  return ret

def get_powers_from_dnd35_db(powerDBpath=os.path.join('srd35-db-SQLite-v1.3', 'dnd35.db') ):
  """http://www.enworld.org/forum/showthread.php?205248-SRD-3-5-Database-SQLite
  """
  conn = sqlite3.connect(powerDBpath)
  curs = conn.cursor()
  #curs.execute('''CREATE TEMPORARY TABLE disciplines (id INTEGER, name varchar(32) );''')
  curs.execute('''SELECT name, discipline,subdiscipline, descriptor, level, xp_cost, manifesting_time, range, target, area, effect, duration, saving_throw,power_resistance, full_text FROM power;''')
  # xp_cost from this database is the entire text after XP Cost:, which makes a certain amount of sense since it includes things like "250 XP for each point by which the object's hardness is altered."
  # A plain integer clearly wouldn't be very useful here, but I think the other database had the right idea: have a boolean for whether there's an XP cost *at all*, and leave the details in the description.
  def fix_XP(xp_cost):
    if xp_cost == 'None': return False
    else: return True
  return [(name, discipline, fix_XP(xp_cost), manifesting_time, spellrange, target, area, effect, duration, saving_throw,power_resistance, full_text) for (name, discipline,subdiscipline, descriptor, level, xp_cost, manifesting_time, spellrange, target, area, effect, duration, saving_throw,power_resistance, full_text) in curs.fetchall()]
"""
they're all from the SRD:
sqlite> select distinct reference from power;
SRD 3.5 PsionicPowersA-C
SRD 3.5 PsionicPowersD-F
SRD 3.5 PsionicPowersG-P
SRD 3.5 PsionicPowersQ-W
"""



def id_from_name(curs, tableName, name):
  """
  This function uses SQL's like instead of exact equality, to enable tricks like passing "Colossal%" to match Colossal+.
  """
  if re.match("\w+$", tableName) is None:
    raise TypeError(tableName + " does not look like a valid SQL table name.")
  curs.execute('''SELECT id from {} WHERE name like ?;'''.format(tableName), (name,) )
  result = curs.fetchone()
  if result is None:
    return None
    #raise IndexError("{} does not appear in the SQL table {}.".format(name, tableName) )
  else: return result[0]
def insert_if_needed(curs, tableName, name, **kwargs):
  """
it is NOT safe to re-insert an entry into a table:
sqlite> create table tbl (id INTEGER PRIMARY KEY NOT NULL, x nchar(1) );
sqlite> insert into tbl (x) values ('a');
sqlite> insert into tbl (x) values ('a');
sqlite> select id,x from tbl;
1|a
2|a
  """
  existingID = id_from_name(curs, tableName, name)
  kwargs['name'] = name
  columnNames,values = zip(*kwargs.items() )
  for col in columnNames:
    if re.match("\w+$", col) is None:
      raise TypeError(col)
  if existingID is not None:
    # Here's the problem: we do legitimately have cases where two different abilities share the same name.
    # For example, the aboleth has a slime special attack while the brine naga has a slime special quality.
    if tableName == "dnd_special_ability": return existingID # hack
    kwargs['id'] = existingID
    curs.execute('''SELECT {} FROM {} WHERE id=:id;'''.format(','.join(columnNames), tableName), kwargs)
    for i,val in enumerate(curs.fetchone() ):
      if val != values[i] and type(val) is not str or val.lower() != values[i].lower():
        raise RuntimeError("{} != {} in row {}".format(val, values[i], kwargs) )
    return existingID
  else:
    assert existingID is None
    commandString = '''INSERT INTO {} ({}) VALUES ({});'''.format(tableName, ','.join(columnNames), ','.join([':'+col for col in columnNames]) )
    #print('commandString =', commandString)
    curs.execute(commandString, kwargs)
    return curs.lastrowid


def insert_psionic_powers(curs):
  srd_id = 116
  curs.execute('''INSERT INTO dnd_rulebook (id, dnd_edition_id, name, abbr, description, year, official_url, slug, published) VALUES (116, 1, "Revised (v.3.5) System Reference Document", "SRD", "The System Reference Document is a comprehensive toolbox consisting of rules, races, classes, feats, skills, various systems, spells, magic items, and monsters compatible with the d20 System version of Dungeons & Dragons and various other roleplaying games from Wizards of the Coast. You may consider this material Open Game Content under the Open Game License, and may use, modify, and distribute it.", 2004, "http://www.wizards.com/default.asp?x=d20/article/srd35", "system-reference-document", ?);''',
    (datetime.date(2004, 5, 21),) )
  curs.execute('''CREATE TEMPORARY TABLE school_backup (id int, name varchar(32), slug varchar(32) );''')
  curs.execute('''INSERT INTO school_backup SELECT id, name, slug FROM dnd_spellschool;''')
  curs.execute('''DROP TABLE dnd_spellschool;''')
  curs.execute('''CREATE TABLE dnd_spellschool (
  id INTEGER PRIMARY KEY NOT NULL,
  name varchar(32) NOT NULL,
  slug varchar(32) NOT NULL
  );''')
  curs.execute('''CREATE UNIQUE INDEX dnd_spellschool_name ON dnd_spellschool(name);''')
  curs.execute('''INSERT INTO dnd_spellschool SELECT id, name, slug FROM school_backup;''')
  curs.execute('''DROP TABLE school_backup;''')
  curs.execute('''INSERT INTO dnd_spellschool (name, slug) VALUES (?, ?)''', ('Psychometabolism', 'psychometabolism') )
  psychometabolismID = curs.lastrowid
  curs.execute('''INSERT INTO dnd_spellschool (name, slug) VALUES (?, ?)''', ('Psychoportation', 'psychoportation') )
  psychoportationID = curs.lastrowid
  curs.execute('''INSERT INTO dnd_spellschool (name, slug) VALUES (?, ?)''', ('Psychokinesis', 'psychokinesis') )
  psychokinesisID = curs.lastrowid
  curs.execute('''INSERT INTO dnd_spellschool (name, slug) VALUES (?, ?)''', ('Metacreativity', 'metacreativity') )
  metacreativityID = curs.lastrowid
  curs.execute('''INSERT INTO dnd_spellschool (name, slug) VALUES (?, ?)''', ('Clairsentience', 'clairsentience') )
  clairsentienceID = curs.lastrowid
  curs.execute('''INSERT INTO dnd_spellschool (name, slug) VALUES (?, ?)''', ('Telepathy', 'telepathy') )
  telepathyID = curs.lastrowid
  curs.execute('''CREATE TEMPORARY TABLE spell_backup (
  id INTEGER PRIMARY KEY NOT NULL,
  added datetime NOT NULL,
  rulebook_id int(11) NOT NULL,
  page smallint(5)  DEFAULT NULL,
  name varchar(64) NOT NULL,
  slug varchar(64) NOT NULL,
  school_id int(11) NOT NULL,
  sub_school_id int(11) DEFAULT NULL,
  verbal_component tinyint(1) NOT NULL DEFAULT 0,
  somatic_component tinyint(1) NOT NULL DEFAULT 0,
  material_component tinyint(1) NOT NULL DEFAULT 0,
  arcane_focus_component tinyint(1) NOT NULL DEFAULT 0,
  divine_focus_component tinyint(1) NOT NULL DEFAULT 0,
  xp_component tinyint(1) NOT NULL DEFAULT 0,
  corrupt_component tinyint(1) NOT NULL DEFAULT 0,
  corrupt_level smallint(5)  DEFAULT NULL,
  meta_breath_component tinyint(1) NOT NULL DEFAULT 0,
  true_name_component tinyint(1) NOT NULL DEFAULT 0,
  extra_components varchar(256) DEFAULT NULL,
  casting_time varchar(256) DEFAULT NULL,
  range varchar(256) DEFAULT NULL,
  target varchar(256) DEFAULT NULL,
  effect varchar(256) DEFAULT NULL,
  area varchar(256) DEFAULT NULL,
  duration varchar(256) DEFAULT NULL,
  saving_throw varchar(128) DEFAULT NULL,
  spell_resistance varchar(64) DEFAULT NULL,
  description longtext NOT NULL,
  description_html longtext NOT NULL DEFAULT "",
  verified tinyint(1) NOT NULL DEFAULT 0,
  verified_author_id int(11) DEFAULT NULL,
  verified_time datetime DEFAULT NULL);''')
  curs.execute('''INSERT INTO spell_backup SELECT id,added,rulebook_id,page,name,slug, school_id,sub_school_id, verbal_component,somatic_component,material_component,arcane_focus_component,divine_focus_component,xp_component, corrupt_component,corrupt_level,meta_breath_component,true_name_component, extra_components, casting_time, range,target,effect,area, duration, saving_throw,spell_resistance, description,description_html, verified,verified_author_id,verified_time FROM dnd_spell;''')
  curs.execute('''DROP TABLE dnd_spell;''')
  curs.execute('''CREATE TABLE dnd_spell (
  id INTEGER PRIMARY KEY NOT NULL,
  added datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  rulebook_id int(11) NOT NULL,
  page smallint(5)  DEFAULT NULL,
  name varchar(64) NOT NULL,
  slug varchar(64) NOT NULL,
  school_id int(11) NOT NULL,
  sub_school_id int(11) DEFAULT NULL,
  verbal_component tinyint(1) NOT NULL DEFAULT 0,
  somatic_component tinyint(1) NOT NULL DEFAULT 0,
  material_component tinyint(1) NOT NULL DEFAULT 0,
  arcane_focus_component tinyint(1) NOT NULL DEFAULT 0,
  divine_focus_component tinyint(1) NOT NULL DEFAULT 0,
  xp_component tinyint(1) NOT NULL DEFAULT 0,
  corrupt_component tinyint(1) NOT NULL DEFAULT 0,
  corrupt_level smallint(5)  DEFAULT NULL,
  meta_breath_component tinyint(1) NOT NULL DEFAULT 0,
  true_name_component tinyint(1) NOT NULL DEFAULT 0,
  extra_components varchar(256) DEFAULT NULL,
  casting_time varchar(256) DEFAULT NULL,
  range varchar(256) DEFAULT NULL,
  target varchar(256) DEFAULT NULL,
  effect varchar(256) DEFAULT NULL,
  area varchar(256) DEFAULT NULL,
  duration varchar(256) DEFAULT NULL,
  saving_throw varchar(128) DEFAULT NULL,
  spell_resistance varchar(64) DEFAULT NULL,
  description longtext NOT NULL DEFAULT "description missing",
  description_html longtext NOT NULL DEFAULT "",
  verified tinyint(1) NOT NULL DEFAULT 0,
  verified_author_id int(11) DEFAULT NULL,
  verified_time datetime DEFAULT NULL,
  CONSTRAINT "verified_author_id_refs_id_283e8e34" FOREIGN KEY ("verified_author_id") REFERENCES "auth_user" ("id"),
  CONSTRAINT "rulebook_id_refs_id_514d0131604a89b" FOREIGN KEY ("rulebook_id") REFERENCES "dnd_rulebook" ("id"),
  CONSTRAINT "school_id_refs_id_5015d8d2133c7ac3" FOREIGN KEY ("school_id") REFERENCES "dnd_spellschool" ("id"),
  CONSTRAINT "sub_school_id_refs_id_75647c3f68dd90be" FOREIGN KEY ("sub_school_id") REFERENCES "dnd_spellsubschool" ("id")
  );''')
  curs.execute('''INSERT INTO dnd_spell SELECT * FROM spell_backup;''')
  # this enables sanitizing, but does not by itself sanitize, so we still have all those varchar '0's in xp_component etc
  # Since casting times and ranges tend to be standardized, it would make more sense to have an intersection table spell_range and an intersection table spell_casting_time...
  # select count(*) from (select distinct casting_time from dnd_spell); returns 60, and a lot of those are probably misspellings or things like "1 action" for 1 standard action
  # For that matter, there are only 375 distinct areas: select count(*) from (select distinct area from dnd_spell);
  curs.execute('''CREATE TABLE dnd_range (
  id INTEGER PRIMARY KEY NOT NULL,
  name varchar(32),
  feetCL0 INTEGER,
  feet_per_level INTEGER
  );''')
  curs.execute('''INSERT INTO dnd_range (name,feetCL0,feet_per_level) VALUES (?,?,?)''',
               ('Close', 25, fraction_to_negative('1/2') ) )
  curs.execute('''INSERT INTO dnd_range (name,feetCL0,feet_per_level) VALUES (?,?,?)''',
               ('Unlimited', eightByteIntMax, eightByteIntMax) )

  curs.execute('''DROP TABLE spell_backup;''')

  # It will be better to get the SRD psionic powers from dnd35.db, but that power table makes everything varchar even level, so will need processing
  for (name, discipline, xp_cost, manifesting_time, spellrange, target, area, effect, duration, saving_throw,power_resistance, full_text) in get_powers_from_dnd35_db():
    slug = name.lower().replace(',','').replace(' ','-')
    curs.execute('''SELECT id FROM dnd_spellschool WHERE name like ?''', (discipline,) )
    schoolID = curs.fetchone()[0]
    curs.execute('''INSERT INTO dnd_spell (rulebook_id, name, slug, school_id, xp_component, casting_time, range, target, effect, area, duration, saving_throw, spell_resistance, description_html) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                 (srd_id, name, slug, schoolID, xp_cost, manifesting_time, spellrange, target, effect, area, duration, saving_throw,power_resistance, full_text) )

  # still have problems with things like defensive precognition/precognition, defensive  
  def insertPower(name, schoolID, url):
    curs.execute('''INSERT INTO dnd_spell (rulebook_id, name, slug, school_id, description_html) VALUES (?, ?, ?, ?, ?)''',
                 (srd_id, name, name.lower().replace(' ', '-'), schoolID, url) )
  insertPower('Defensive Precognition', clairsentienceID, "http://www.d20srd.org/srd/psionic/powers/precognitionDefensive.htm")
  insertPower('Offensive Precognition', clairsentienceID, "http://www.d20srd.org/srd/psionic/powers/precognitionOffensive.htm")
  insertPower('Offensive Prescience', clairsentienceID, "http://www.d20srd.org/srd/psionic/powers/precognitionOffensive.htm")

  curs.execute('''INSERT INTO dnd_spell (added, rulebook_id, name, school_id, description, description_html, slug) VALUES (?, ?, ?, ?, ?, ?, ?)''',
               (datetime.datetime.now(), srd_id, "Ego Whip", telepathyID, "Your rapid mental lashings assault the ego of your enemy, debilitating its confidence. The target takes 1d4 points of Charisma damage, or half that amount (minimum 1 point) on a successful save. A target that fails its save is also dazed for 1 round.", "http://www.d20srd.org/srd/psionic/powers/egoWhip.htm", 'ego-whip') )
  curs.execute('''INSERT INTO dnd_spell (added, rulebook_id, name, slug, school_id, description, description_html) VALUES (?, ?, ?, ?, ?, ?, ?)''',
               (datetime.datetime.now(), srd_id, "Id Insinuation", 'id-insinuation', telepathyID, "As the confusion spell, except as noted here.", "http://www.d20srd.org/srd/psionic/powers/idInsinuation.htm") )
  curs.execute('''INSERT INTO dnd_spell (added, rulebook_id, name, slug, school_id, description, description_html) VALUES (?, ?, ?, ?, ?, ?, ?)''',
               (datetime.datetime.now(), srd_id, "Disable", 'disable', telepathyID, "You broadcast a mental compulsion that convinces one or more creatures of 4 Hit Dice or less that they are disabled. Creatures with the fewest HD are affected first. Among creatures with equal Hit Dice, those who are closest to the power's point of origin are affected first. Hit Dice that are not sufficient to affect a creature are wasted. Creatures that are rendered helpless or are destroyed when they reach 0 hit points cannot be affected.", "http://www.d20srd.org/srd/psionic/powers/disable.htm") )
  curs.execute('''INSERT INTO dnd_spell (added, rulebook_id, name, slug, school_id, description, description_html) VALUES (?, ?, ?, ?, ?, ?, ?)''',
               (datetime.datetime.now(), srd_id, "False Sensory Input", 'false-sensory-input', telepathyID, "You have a limited ability to falsify one of the subject's senses. The subject thinks she sees, hears, smells, tastes, or feels something other than what her senses actually report. You can't create a sensation where none exists, nor make the subject completely oblivious to a sensation, but you can replace the specifics of one sensation with different specifics. For instance, you could make a human look like a dwarf (or one human look like another specific human), a closed door look like it is open, a vat of acid smell like rose water, a parrot look like a bookend, stale rations taste like fresh fruit, a light pat feel like a dagger thrust, a scream sound like the howling wind, and so on.", "http://www.d20srd.org/srd/psionic/powers/falseSensoryInput.htm") )
  curs.execute('''INSERT INTO dnd_spell (added, rulebook_id, name, slug, school_id, description_html) VALUES (?, ?, ?, ?, ?, ?)''',
               (datetime.datetime.now(), srd_id, "Mental Disruption", 'mental-disruption', telepathyID, "http://www.d20srd.org/srd/psionic/powers/mentalDisruption.htm") )
  curs.execute('''INSERT INTO dnd_spell (added, rulebook_id, name, slug, school_id, description_html) VALUES (?, ?, ?, ?, ?, ?)''',
               (datetime.datetime.now(), srd_id, "Mindlink", 'mindlink', telepathyID, "http://www.d20srd.org/srd/psionic/powers/mindlink.htm") )
  curs.execute('''INSERT INTO dnd_spell (added, rulebook_id, name, slug, school_id, description_html) VALUES (?, ?, ?, ?, ?, ?)''',
               (datetime.datetime.now(), srd_id, "Psionic Dominate", 'dominate-psionic', telepathyID, "http://www.d20srd.org/srd/psionic/powers/dominatePsionic.htm") )
  #curs.execute('''INSERT INTO dnd_spell (rulebook_id, name, slug, school_id, description_html) VALUES (?, ?, ?, ?, ?)''',
  #             (srd_id, "Thought Shield", 'thought-shield', telepathyID, "http://www.d20srd.org/srd/psionic/powers/thoughtShield.htm") )
  curs.execute('''INSERT INTO dnd_spell (rulebook_id, name, slug, school_id, description_html) VALUES (?, ?, ?, ?, ?)''',
               (srd_id, "Psionic Modify Memory", 'modify-memory-psionic', telepathyID, "http://www.d20srd.org/srd/psionic/powers/modifyMemoryPsionic.htm") )
  curs.execute('''INSERT INTO dnd_spell (rulebook_id, name, slug, school_id, description_html) VALUES (?, ?, ?, ?, ?)''',
               (srd_id, "Cloud Mind", 'cloud-mind', telepathyID, "http://www.d20srd.org/srd/psionic/powers/cloudMind.htm") )
  #curs.execute('''INSERT INTO dnd_spell (rulebook_id, name, slug, school_id, description_html) VALUES (?, ?, ?, ?, ?)''',
  #             (srd_id, "Read Thoughts", 'read-thoughts', telepathyID, "http://www.d20srd.org/srd/psionic/powers/readThoughts.htm") )
  insertPower('Detect Hostile Intent', telepathyID, "http://www.d20srd.org/srd/psionic/powers/detectHostileIntent.htm")
  curs.execute('''INSERT INTO dnd_spell (rulebook_id, name, slug, school_id, description_html) VALUES (?, ?, ?, ?, ?)''',
               (srd_id, "Remote Viewing", 'remote-viewing', clairsentienceID, "http://www.d20srd.org/srd/psionic/powers/remoteViewing.htm") )
  curs.execute('''INSERT INTO dnd_spell (rulebook_id, name, slug, school_id, description_html) VALUES (?, ?, ?, ?, ?)''',
               (srd_id, "Aura Sight", 'aura-sight', clairsentienceID, "http://www.d20srd.org/srd/psionic/powers/auraSight.htm") )
  curs.execute('''INSERT INTO dnd_spell (rulebook_id, name, slug, school_id, description_html) VALUES (?, ?, ?, ?, ?)''',
               (srd_id, "Detect Psionics", 'detect-psionics', clairsentienceID, "http://www.d20srd.org/srd/psionic/powers/detectPsionics.htm") )
  insertPower('Mental Barrier', clairsentienceID, "http://www.d20srd.org/srd/psionic/powers/mentalBarrier.htm")
  curs.execute('''INSERT INTO dnd_spell (rulebook_id, name, slug, school_id, description_html) VALUES (?, ?, ?, ?, ?)''',
               (srd_id, "Psionic Plane Shift", 'plane-shift-psionic', psychoportationID, "http://www.d20srd.org/srd/psionic/powers/planeShiftPsionic.htm") )
  curs.execute('''INSERT INTO dnd_spell (rulebook_id, name, slug, school_id, description_html) VALUES (?, ?, ?, ?, ?)''',
               (srd_id, "Psionic Daze", 'daze-psionic', telepathyID, "http://www.d20srd.org/srd/psionic/powers/dazePsionic.htm") )
  curs.execute('''INSERT INTO dnd_spell (rulebook_id, name, slug, school_id, description_html) VALUES (?, ?, ?, ?, ?)''',
               (srd_id, "Psionic Charm", 'charm-psionic', telepathyID, "http://www.d20srd.org/srd/psionic/powers/charmPsionic.htm") )
  curs.execute('''INSERT INTO dnd_spell (rulebook_id, name, slug, school_id, description_html) VALUES (?, ?, ?, ?, ?)''',
               (srd_id, "Psionic Dominate", 'dominate-psionic', telepathyID, "http://www.d20srd.org/srd/psionic/powers/dominatePsionic.htm") )
  curs.execute('''INSERT INTO dnd_spell (rulebook_id, name, slug, school_id, description_html) VALUES (?, ?, ?, ?, ?)''',
               (srd_id, "Psionic Suggestion", 'suggestion-psionic', telepathyID, "http://www.d20srd.org/srd/psionic/powers/suggestionPsionic.htm") )
  insertPower('Far Hand', psychokinesisID, "http://www.d20srd.org/srd/psionic/powers/farHand.htm")
  insertPower('Concealing Amorpha', metacreativityID, "http://www.d20srd.org/srd/psionic/powers/concealingAmorpha.htm")
  insertPower('Entangling Ectoplasm', metacreativityID, "http://www.d20srd.org/srd/psionic/powers/entanglingEctoplasm.htm")
  #insertPower('Telekinetic Thrust', psychokinesisID, "http://www.d20srd.org/srd/psionic/powers/telekineticThrust.htm")
  insertPower('Catfall', psychoportationID, "http://www.d20srd.org/srd/psionic/powers/catfall.htm")
  #insertPower('Concussion Blast', psychokinesisID, "http://www.d20srd.org/srd/psionic/powers/concussionBlast.htm")
  insertPower('Inertial Armor', psychokinesisID, "http://www.d20srd.org/srd/psionic/powers/inertialArmor.htm")
  insertPower('Aversion', telepathyID, "http://www.d20srd.org/srd/psionic/powers/aversion.htm")
  #insertPower('Mind Thrust', telepathyID, "http://www.d20srd.org/srd/psionic/powers/mindThrust.htm")
  insertPower('Exhalation of the Black Dragon', psychometabolismID, "http://www.d20srd.org/srd/psionic/powers/exhalationoftheBlackDragon.htm")
  insertPower('Body Purification', psychometabolismID, "http://www.d20srd.org/srd/psionic/powers/bodyPurification.htm")
  insertPower('Reach', psychometabolismID, "http://archive.wizards.com/default.asp?x=dnd/psm/20010928a")

  insertPower('Corrupt Water', 7, "http://www.d20srd.org/srd/monsters/dragonTrue.htm#blackDragon")
  insertPower('Charm Reptiles', 4, "http://www.d20srd.org/srd/monsters/dragonTrue.htm#blackDragon")
  insertPower('Destroy Water', 4, "http://www.d20srd.org/srd/monsters/dragonTrue.htm#blueDragon")
  insertPower('Luck Bonus', 7, "http://www.d20srd.org/srd/monsters/dragonTrue.htm#goldDragon")
  insertPower('Detect Gems', 3, "http://www.d20srd.org/srd/monsters/dragonTrue.htm#goldDragon")
  insertPower('Create Wine', 2, "http://www.d20srd.org/srd/monsters/genie.htm#djinni")
  insertPower('Dreamscape', 2, "http://www.d20srd.org/srd/epic/spells/dreamscape.htm")
  insertPower('Nailed To The Sky', 2, "http://www.d20srd.org/srd/epic/spells/nailedToTheSky.htm")
  insertPower('Hellball', 5, "http://www.d20srd.org/srd/epic/spells/hellball.htm")
  insertPower('Enslave', 4, "http://www.d20srd.org/srd/epic/spells/enslave.htm")
  insertPower('Safe Time', 2, "http://www.d20srd.org/srd/epic/spells/safeTime.htm")
  insertPower('Time Duplicate', 2, "http://www.d20srd.org/srd/epic/spells/timeDuplicate.htm")
  insertPower('contingent recall and resurrection', 2, "http://www.d20srd.org/srd/epic/monsters/hoaryHunter.htm")
  insertPower('contingent resurrection', 2, "http://www.d20srd.org/srd/epic/spells/contingentResurrection.htm")
  insertPower('Ruin', 7, "http://www.d20srd.org/srd/epic/spells/ruin.htm")
  insertPower('Peripety', 1, "http://www.d20srd.org/srd/epic/spells/peripety.htm")
  insertPower('Spell Worm', 4, "http://www.d20srd.org/srd/epic/spells/spellWorm.htm")
  insertPower('Demise Unseen', 6, "http://www.d20srd.org/srd/epic/spells/demiseUnseen.htm")

  # Complete Psionic:
  insertPower('Energy Arc', psychokinesisID, "A cone of the chosen type of energy shoots from your fingertips. Any creature in the area of effect takes 1d4 points of damage.")
  insertPower('Primal Fear', telepathyID, "shaken for 1 round. This effect doesn't stack with other fear effects.")

  # Frostburn and Sandstorn:
  insertPower('Energy Emanation', psychokinesisID, "1d6 points of energy damage to all creatures within the area every round. Creatures in the area must make a new Fortitude save each round.")
  insertPower('Energy Flash', psychokinesisID, "5d6 points of damage to the creature touched, doing cold, electricity, fire, or sonic damage. In addition to the energy damage, the target is dazed for 1 round on a failed Fortitude save (the same save that determines full or half damage).")
  insertPower('Fish Cloud', 2, "When submerged in water, a vodyanoi can summon a huge school of magic fish to provide concealment (similar to the fog cloud spell). This school of fish swims around the point the vodyanoi designates in a 20-foot radius. This cloud of fish obscures all sight, including darkvision, beyond 5 feet. A creature within 5 feet has concealment. Creatures farther away have total concealment. A strong current disperses the cloud of fish in 4 rounds. A very strong current disperses the cloud of fish in 1 round. The fish created by this spell are formed by magic; they are not real animal, and objects and energies pass through them as  though they were not there. A vodyanoi can summon a fish cloud three times per day. The fish cloud remains for 40 minutes or until dispersed or dispelled.")
  insertPower('Global Warming', 5, "You increase the temperature of the region, drying up water and baking the soil within a 100-mile-radius area.")
  insertPower('Inconstant Location', psychoportationID, "At the beginning of your turn, as a swift action, you can teleport yourself to any other space to which you have line of sight, so long as that space is no farther than you could move in normal move action.")

  # Tome of Magic:
  insertPower('Black Candle', 5, "This mystery functions like the spell light or the spell darkness.")
  insertPower('Dusk and Dawn', 5, "You make a dark area lighter or a light area darker, blanketing the affected area in shadowy illumination.")
  insertPower('Pass Into Shadow', 2, "This mystery functions like the spell plane shift, except that your destination or origination must be the Plane of Shadow.")
  insertPower('Bolster', 7, "You grant the subject 5 temporary hit points for each of its Hit Dice (maximum 75).")
  insertPower('Sight Eclipsed', 8, "While this mystery is in effect, you can attempt Hide checks even while being observed, just as if you had cover or concealment for the purpose of this determination.")
  insertPower('Umbral Body', 7, "You gain the incorporeal subtype (see page 164) and all advantages and traits associated with it.")
  insertPower('Potent Word of Nurturing', 12, "You grant a creature fast healing 10.")
  insertPower('Critical Word of Nurturing', 12, "you utter the reverse form of the life-giving words. You deal 8d6 points of damage to the subject.")
  insertPower('Incarnation of Angels', 7, "The target gains the celestial creature template (MM 31). The target gains the fi endish creature template (MM 107).")
  insertPower("Archer's Eye", 7, "Your target's ranged attacks ignore penalties for concealment because her aim sharpens to focus on the unconcealed parts of her foe.")
  insertPower("Shockwave", 5, "A violent shock wave travels through the air, and creatures in the area must make Fortitude saves or be knocked prone and take 1d4 points of nonlethal damage.")
  insertPower("Preternatural Clarity", 3, "+5 insight bonus on any single attack roll, opposed ability or skill check, or saving throw. When your target uses the insight bonus, those within 10 feet of her can hear an echo of your original utterance, even if you're no longer present. Activating the effect is an immediate action. The target can choose to apply the bonus after she has rerolled the d20, but before the Dungeon Master reveals the result of the check.")
  insertPower("Morale Boost", 3, "This utterance functions as the remove fear spell (PH 271). Your target becomes frightened (DMG 301) by the susurrant Truespeech being whispered in its ear.")
  insertPower("Hidden Truth", 3, "You grant the target a +10 bonus on a single Knowledge check and enable her to use the skill, even if untrained. If the target has bardic knowledge, lore, or a similar class feature, this bonus can apply to that check instead. Your target gains a +10 bonus on a single Bluff check made before the duration of the utterance expires.")

  # Kingdoms of Kalamar Player's Guide
  insertPower("Disinter", 7, "Kalamar: brings to the surface any item that you buried")
  insertPower("Silken Grasp", 7, "Kalamar: +20 grapple initial hold")
  insertPower("Cannibalize", 6, "http://www.d20pfsrd.com/magic/3rd-party-spells/kobold-press-open-design/cannibalize/")
  insertPower('Caustic Bile', psychometabolismID, "???")
  insertPower('Insatiable Hunger', psychometabolismID, "???")

  insertPower('Regenerate Worldskin 50', 2, "As a standard action, Ragnorra can initiate regeneration in any worldskin feature (see page 102). This ability has unlimited range. The growth regains 50 hit points per round.")
  insertPower('Regenerate Worldskin', 2, "As a standard action, Ragnorra can initiate regeneration in any worldskin feature (see page 102). This ability has unlimited range. The growth regains 50 hit points per round.")
  insertPower('Skincasting', 2, "As a standard action, Ragnorra can activate the ability of any worldskin feature (see page 102) within 1,000 feet.")
  insertPower('Mass Aversion', telepathyID, "An anathema creates a compulsion effect targeting all enemies within 30 feet. The targets must succeed on a Will save (DC 27) or gain an aversion to snakes for 10 minutes. Affected subjects must stay at least 20 feet from any snake, yuan-ti, or ti-khana creature (described earlier in this book), whether alive or dead; if already within 20 feet, they move away. A subject can overcome the compulsion by succeeding on another Will save (DC 27), but still suffers from deep anxiety. This causes a -4 reduction to Dexterity until the effect wears off or the subject is no longer within 20 feet of a snake, yuan-ti, or ti-khana creature. This ability is otherwise similar to antipathy as cast by a 16th-level sorcerer.")

class Monster(object):
  def __init__(self, xls_row):
    self.name = xls_row[0].value
    self.size = xls_row[1].value
    self.type_name = xls_row[2].value
    if xls_row[3].value == '': self.subtypes = [] # ''.split(',') is not an empty list, but rather a list containing ''
    else: self.subtypes = [fix_subtype(subtype) for subtype in xls_row[3].value.replace(' or ', ', ').replace('[alignment subtype]', 'Good, Evil, Lawful, Chaotic').split(',')]
    for subtype in self.subtypes: assert subtype != ''
    self.HitDice = fraction_to_negative(xls_row[4].value)
    swimflyburrowcrawl = xls_row[7].value
    #touchAC = int(xls_row[9])
    #flatfootedAC = int(xls_row[10])
    # http://stackoverflow.com/questions/2415398/can-i-set-a-formula-for-a-particular-column-in-sql

    self.strength = integer_or_non(xls_row[20].value)
    self.dexterity = integer_or_non(xls_row[21].value)
    self.constitution = integer_or_non(xls_row[22].value)
    self.intelligence = integer_or_non(xls_row[23].value)
    self.wisdom = int(xls_row[24].value)
    self.charisma = int(xls_row[25].value)
    default_alignment_string = xls_row[28].value # can be something like "NG or NE"
    if len(default_alignment_string) < 2: raise RuntimeError(default_alignment_string)
    if default_alignment_string == 'Any': default_alignment_string = 'NN'
    #print('default_alignment_string =', default_alignment_string)
    self.lawChaosID = lawChaosToInt[default_alignment_string[0]]
    self.goodEvilID = goodEvilToInt[default_alignment_string[1]]
    if xls_row[29].value == '-': self.challenge_rating = 0
    else: self.challenge_rating = fraction_to_negative(xls_row[29].value)
    self.rulebook_abbrev = xls_row[30].value

    commaSeparatedSpecialAttacks = xls_row[14].value
    #print('commaSeparatedSpecialAttacks =', commaSeparatedSpecialAttacks)
    self.specialAttacks = [ab.strip() for ab in commaSeparatedSpecialAttacks.split(',')]
    #print('self.specialAttacks =', self.specialAttacks)
    commaSeparatedSpecialQualities = xls_row[16].value
    self.specialQualities = [ab.strip() for ab in commaSeparatedSpecialAttacks.split(',')]

    self.SpellLikeAbilities = list()
    SLAstring = xls_row[15].value
    if 'SLAs' in self.specialAttacks or 'PLAs' in self.specialAttacks:
      if SLAstring == '':
        if self.name=="Devil, Ice (Gelugon)":
          SLAstring = "CL13, At will - cone of cold (DC 20), fly, ice storm (DC 19), greater teleport (self plus 50 pounds of objects only), persistent image (DC 20), unholy aura (DC 23), wall of ice"
      if self.name == 'Githyanki':
        SLAstring = "ML=HD/2, 3/day - far hand; 3/day - concealing amorpha; 3/day - dimension door; 3/day - telekinetic thrust; 1/day - plane shift"
      elif self.name == 'Githzerai':
        SLAstring = "ML=HD/2, 3/day - catfall, concussion blast, inertial armor; 1/day - plane shift"
      elif self.name == 'Tayfolk, Tayling':
        SLAstring = "CL=lvl, 3/day - cure minor wounds, mage hand; 3/day - cat's grace; 3/day - haste; 3/day - polymorph"
      elif self.name == "Planetouched, D'hin'ni":
        SLAstring = "CL1, at will - prestidigitation; 1/day - gust of wind, whispering wind, wind wall"
      elif self.name == 'Gingwatzim, Naranzim':
        SLAstring = "CL5, at will - color spray, ghost sound, invisibility (self only), Nystul's magic aura, silent image, ventriloquism; 3/day - blur (self only), hypnotic pattern, minor image, mirror image, misdirection; 1/day - displacement, invisibility sphere, major image (self only); 1/day - greater invisibility, phantasmal killer, rainbow pattern; 1/day - dream, nightmare, persistent image"
      elif self.name == "Titan":
        SLAstring = "CL20, at will - chain lightning, charm monster, cure critical wounds, fire storm, greater dispel magic, hold monster, invisibility, invisibility purge, levitate, persistent image; 3/day - etherealness, word of chaos, summon nature's ally IX; 1/day - gate, maze, meteor swarm; at will - daylight, holy smite, remove curse; 1/day - greater restoration; at will - bestow curse, deeper darkness, unholy blight; 1/day - Bigby's crushing hand"
      elif self.name == "Titan, Stormbringer":
        SLAstring = "CL20, at will - chain lightning, charm monster, control weather, cure critical wounds, fire storm, gaseous form, greater dispel magic, hold monster, invisibility, invisibility purge, water breathing, wind wall; 3/day - whirlwind, wind walk, word of chaos; 1/day - gate, maze, storm of vengeance; at will - daylight, holy smite, remove curse; 1/day - greater restoration; at will - bestow curse, deeper darkness, unholy blight; 1/day - Bigby's crushing hand"
      elif self.name == "Phoenix":
        SLAstring = "CL20, at will - blindness, blink, blur, color spray, cure light wounds, dancing lights, death ward, find the path, find traps, fire seeds, heal, invisibility, misdirection, neutralize poison, produce flame, remove fear, remove curse, see invisibility; 1/day - incendiary cloud, reincarnate, pyrotechnics, summon nature's ally IX, veil, wall of fire; CL40, at will - dismissal, dispel evil, dispel magic"
      elif self.name == "Grisgol" or self.name == "Nature Spirit, Large":
        SLAstring = '' # varies by construction, skip
      elif self.name == "Thaumavore":
        SLAstring = "CLHD, 10/day - comprehend languages, protection from evil, ray of enfeeblement, sleep, invisibility, touch of idiocy, blink, deep slumber, confusion, dimension door, symbol of sleep, antimagic field, plane shift"
      elif self.name == "Ssvaklor":
        SLAstring = "ML7, 1/day - aversion (duration 10 hours*), control light, entangling ectoplasm, id insinuation (up to 4 creatures*), psionic freedom of movement"
      elif self.name[:9] == "Zeitgeist":
        SLAstring = "CL20, at will - animate objects, call lighting storm, calm emotions, confusion, contagion, fear, impeding stones, make whole, move earth, produce flame, remove disease, repel metal or stone, repel wood, soften earth and stone, spike stones, stone shape, wall of iron, wall of stone, wood shape, zone of peace"
      elif self.name == "Gibbering Orb":
        SLAstring = "CL27, at will - wish (takes pit fiend SLA and makes it at will)"
      elif self.name == "Bacchae":
        SLAstring = "CL7, 3/day - charm person, Tasha's hideous laughter; 1/day - crushing despair, fear, good hope, rage"
      elif self.name == "Kelpie":
        SLAstring = "CL7, at will - detect thoughts; 3/day - charm person, crushing despair, fear, good hope, rage"
      elif self.name == "Archon, Word":
        SLAstring = "TL10, 10/day - potent word of nurturing, incarnation of angels, archer's eye; 10/day - shockwave"
      elif self.name == "Devil, Logokron":
        SLAstring = "CL15, at will - major image, greater teleport (self +50lbs only), critical word of nurturing (reverse only), preternatural clarity, morale boost, hidden truth"
      elif self.name == "Demon, Carnevus":
        SLAstring = "CL8 (choose one from each set per individual) 3/day - charm person, disguise self, magic missile, sleep; 3/day - invisibility, Melf's acid arrow, spider climb, web; 3/day - fireball, hold person, lightning bolt, vampiric touch; 3/day - Evard's black tentacles, lesser globe of invulnerability, ice storm, shadow conjuration"
      elif self.name == "Demon, Turagathshnee":
        SLAstring = "CL13, at will - blasphemy, deeper darkness, desecrate, detect good, detect magic, greater teleport (self +50lbs only); 3/day - slow consumption; 1/day - enervation"
      elif self.name == "Shirokinukatsukami":
        SLAstring = "CL14, at will - astral projection, dream, dream sight, gaseous form, invisibility, magic circle against evil, greater teleport (self +50lbs only); 3/day - cloud trapeze (self +50lbs only), dispel evil, dominate monster; 1/day - heal, raise dead; at will - detect evil, detect thoughts, discern shapechanger"
      elif ', Emprix' in self.name:
        SLAstring = "CL12, at will - aid, continual flame, cure light wounds, daylight, detect magic, dispel magic, flare, holy aura, remove disease, remove fear; CL17, at will - charm person, charm monster, confusion, crushing despair, daze, good hope, rage, suggestion; 3/day - mass charm; 1/month - geas/quest; CL15, at will - detect chaos, detect evil, see invisibility, true seeing"
      elif self.name == "Dread, Greater":
        SLAstring = "CL20, at will - detect magic, blasphemy, deeper darkness, desecrate, detect good, detect law, greater dispel magic, fear, pyrotechnics, read magic, suggestion, symbol of death, symbol of fear, symbol of insanity, symbol of fear, symbol of persuasion, symbol of sleep, symbol of stunning, symbol of weakness, telekinesis, greater teleport (self +50lbs only), tongues (self only), unhallow, unholy aura, unholy blight, wall of fire; 3/day - magic missile; 1/day - fire storm, implosion"
    if self.name == "Pech":
        SLAstring = "CL4, 4/day - stone shape, stone tell; 1/day - wall of stone (requires four pechs), stone to flesh (requires eight pechs)"
    if SLAstring != '':
      SLAstring = SLAstring.strip().replace('; 1 day - ', '; 1/day - ').replace('; 1/day 0 ', '; 1/day - ').replace('; 1d3/day - ', '; 1/day - ')
      #SLAstring = SLAstring.replace('LotEM: 4th', '10/day').replace('LofPM - 1st', '10/day')
      if SLAstring[-1] == '.': SLAstring = SLAstring[:-1]
      SLAstring = SLAstring.replace(', ;', ';')
      # If no caster level is specified, the caster level is equal to the creature's Hit Dice.
      SLAstring = SLAstring.replace('CL unknown', 'CLHD')
      #print('split this:', SLAstring)
      split = freqChangeRE.split(SLAstring)
      if split[0] == '': split = split[1:]
      for new_level_or_new_freq_or_comma_separated_spells in split:
        #print('REsplit freqGroup =', new_level_or_new_freq_or_comma_separated_spells)
        if new_level_or_new_freq_or_comma_separated_spells is None: continue # capturing the group for caster level means ALWAYS capture that group even though it's optional, so when frequency is changed and caster level is not changed we'll get a None, annoying
        if new_level_or_new_freq_or_comma_separated_spells[:7].lower() == 'at will':
          currentUsesPerDay = 127
          continue
        if new_level_or_new_freq_or_comma_separated_spells[-5:] == '/hour':
          assert int(new_level_or_new_freq_or_comma_separated_spells[:-5]) == 1
          currentUsesPerDay = 24
          continue
        if new_level_or_new_freq_or_comma_separated_spells[-4:] == '/day':
          currentUsesPerDay = int(new_level_or_new_freq_or_comma_separated_spells[:-4])
          continue
        if new_level_or_new_freq_or_comma_separated_spells[-5:] == '/week':
          assert int(new_level_or_new_freq_or_comma_separated_spells[:-5]) == 1
          currentUsesPerDay = -7
          continue
        if new_level_or_new_freq_or_comma_separated_spells[-7:] == '/tenday':
          assert int(new_level_or_new_freq_or_comma_separated_spells[:-7]) == 1
          currentUsesPerDay = -10
          continue
        if new_level_or_new_freq_or_comma_separated_spells[-6:] == '/month':
          assert int(new_level_or_new_freq_or_comma_separated_spells[:-6]) == 1
          currentUsesPerDay = -30
          continue
        if new_level_or_new_freq_or_comma_separated_spells[-5:] == '/year':
          assert int(new_level_or_new_freq_or_comma_separated_spells[:-5]) == 1
          currentUsesPerDay = -127#-365
          continue
        if new_level_or_new_freq_or_comma_separated_spells[-8:] == '/century':
          assert int(new_level_or_new_freq_or_comma_separated_spells[:-8]) == 1
          currentUsesPerDay = -127#-36500
          continue
        matchObj = casterLevelRE.match(new_level_or_new_freq_or_comma_separated_spells)
        if matchObj is not None: # this is a new caster level
          assert matchObj.group(1) is not None
          currentCL = matchObj.group(1)
          continue
        for spell,parenthetical in parse_comma_separated_spells(new_level_or_new_freq_or_comma_separated_spells):
          self.SpellLikeAbilities.append( (spell, currentCL, currentUsesPerDay, parenthetical) )
      """
      matchObj = casterLevelRE.match(SLAstring)
      assert matchObj is not None
      CorM = matchObj.group(1)
      assert CorM in ('C', 'M')
      defaultCL = matchObj.group(2)
      print('The default caster level for', self.name, 'is', defaultCL, 'but this can be overridden by individual clauses.')
      #frequencies = freqGroupRE.findall(SLAstring)
      #for i,matchObj in enumerate(frequencies): print('matchObj = ', matchObj)
      #freqGroups = [SLAstring[frequencies[i].end():frequencies[i+1].start()] for i,matchObj in enumerate(frequencies)]
      SLAfreqs = SLAstring.split('; ')
      for freqGroup in SLAfreqs:
        matchObj = casterLevelRE.match(freqGroup)
        if matchObj is not None:
          assert freqGroup[matchObj.end():matchObj.end()+2] == ', '
          thisClauseCL = matchObj.group(2)
          freqGroup = freqGroup[matchObj.end()+2:]
        else:
          thisClauseCL = defaultCL
        print('freqGroup =', freqGroup)
        freq, commaSeparatedSpells = freqGroup.split('-')
        freq = freq.strip()
        if freq == 'at will':
          usesPerDay = 127 # max can store in single-byte signed int
        else:
          assert freq[-4:] == '/day'
          usesPerDay = int(freq[:-4])
        spells = [spell.strip() for spell in noUnparenthesizedCommasRE.findall(commaSeparatedSpells)]
        #print('spells =', spells)
        for spell in spells:
          matchObj = parentheticalRE.search(spell)
          if matchObj is not None:
            assert matchObj.end() == len(spell)
            assert spell[matchObj.start()-1] == ' '
            parenthetical = matchObj.group(1)
            spell = spell[:matchObj.start()-1]
          else:
            parenthetical = None
          self.SpellLikeAbilities.append( (spell, thisClauseCL, usesPerDay, parenthetical) )
        """
        #quoteParens = commaSeparatedSpells.replace('(', '"(').replace(')', ')"')
        # Quoting parentheses does not work. I think csv only permits quotes at the beginning of a field, which makes csv near useless.
        #print('quoteParens =', quoteParens)
        # csv.reader(['goodbye, "this, is row 3", foo3'], skipinitialspace=True).__next__()
        # csv.reader(['disable "(30ft cone, 12HD*)", false sensory input "(five targets*)", mental disruption "(20ft radius*)", mindlink "(unwilling, 9 targets*)"'], skipinitialspace=True).__next__()
        #onlyOneRow = csv.reader([quoteParens], skipinitialspace=True).__next__() # must use skipinitialspace for quoting to work http://stackoverflow.com/questions/6879596/why-is-the-python-csv-reader-ignoring-double-quoted-fields
        #onlyOneRow = [spell.replace('"(', '(').replace(')"', ')') for spell in onlyOneRow]
        #print('onlyOneRow=', onlyOneRow)
  def insert_into(self, curs):
    #print('rulebook_abbrev =', self.rulebook_abbrev)
    curs.execute('''SELECT id from dnd_rulebook where abbr=?;''',
                 (self.rulebook_abbrev,) )
    #print('rulebook_id from dnd_rulebook =', curs.fetchone() )
    self.size = self.size.rstrip('+.')
    #curs.execute('''SELECT id from dnd_racesize WHERE name like ?''', (self.size + '%',) )
    #size_id = curs.fetchone()[0]
    size_id = id_from_name(curs, 'dnd_racesize', self.size + '%')
    assert size_id is not None
    #curs.execute('''SELECT id from dnd_monstertype WHERE name=?''', (self.type_name,) )
    #type_id = curs.fetchone()[0]
    type_id = id_from_name(curs, 'dnd_monstertype', self.type_name)
    assert type_id is not None
    curs.execute('''INSERT INTO dnd_monster
                 (name, size_id, type_id, hit_dice, strength, dexterity, constitution, intelligence, wisdom, charisma, challenge_rating, law_chaos_id)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (self.name, size_id, type_id, self.HitDice, self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom, self.charisma, self.challenge_rating, self.lawChaosID) )
    monster_id = curs.lastrowid
    for subtype in self.subtypes:
      if subtype[:9] == 'Augmented': subtype = 'Augmented'
      if subtype == self.name: continue
      subtype_id = id_from_name(curs, 'dnd_monstersubtype', subtype)
      if subtype_id is None: raise IndexError(self.name + subtype)
      curs.execute('''INSERT INTO monster_subtype (monster_id, subtype_id) VALUES (?, ?);''', (monster_id, subtype_id) )
    for attack in self.specialAttacks:
      ability_id = insert_if_needed(curs, 'dnd_special_ability', attack, special_attack=1)
      curs.execute('''INSERT INTO monster_special_ability (monster_id, special_ability_id) VALUES (?, ?);''', (monster_id, ability_id) )
    for quality in self.specialQualities:
      if quality == "LLV": quality = "Low-Light Vision"
      elif darkvisionRE.match(quality): quality = "Darkvision"
      elif damageReductionRE.match(quality): quality = "Damage Reduction"
      elif spellResistanceRE.match(quality): quality = "Spell Resistance"
      ability_id = insert_if_needed(curs, 'dnd_special_ability', attack, special_attack=0)
      curs.execute('''INSERT INTO monster_special_ability (monster_id, special_ability_id) VALUES (?, ?);''', (monster_id, ability_id) )
    for (spellName, CL, usesPerDay, parenthetical) in self.SpellLikeAbilities:
      # probably want date of monster rulebook and take latest
      try:
        spell_id = spell_name_to_id(curs, spellName)
      except KeyError as E:
        if 'mephit' in self.name.lower(): continue
        else: raise
      if CL[:2] == 'HD' or CL[:3]=='lvl':
        caster_level_scales_with_HD = True
        if 'min' in CL:
          assert re.compile("\(min(\d)\)").match(CL[-6:])
          casterLevel = int(CL[-2])
        else:
          casterLevel = self.HitDice
          if '/' in CL:
            assert CL[:4] == 'HD/2'
            casterLevel = self.HitDice/2
      else:
        casterLevel = int(CL[:2])
        caster_level_scales_with_HD = False
      curs.execute('''INSERT INTO monster_spell_like_ability (monster_id, spell_id, caster_level, caster_level_scales_with_HD, uses_per_day, parenthetical)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                   (monster_id, spell_id, casterLevel, caster_level_scales_with_HD, usesPerDay, parenthetical) )
# Colossal+ Although there is no size category larger than Colossal, the oldest epic dragons deal more damage with their attacks than other Colossal dragons, as shown on the Epic Dragon Face and Reach and Epic Dragon Attacks tables below.
# So Colossal+ can be folded into Colossal.

# Creatures who could not be played in a default-campaign-setting game without adaptation have been omitted. This largely means outsiders native to planes unique to other settings.

# http://stackoverflow.com/questions/4055564/what-does-the-number-in-parenthesis-really-mean
# The number after INT is in base 10, not base 2.
# You get no performance improvement if you use CHAR against VARCHAR in one field, but the table contains other fields that are VARCHAR.
# Slug is used to make a name that is not acceptable for various reasons - e.g. containing special characters, too long, mixed-case, etc. - appropriate for the target usage. What target usage means is context dependent
# FOREIGN KEY https://www.sqlite.org/foreignkeys.html

# In SQLite, a column with type INTEGER PRIMARY KEY is an alias for the ROWID https://www.sqlite.org/autoinc.html
# On an INSERT, if the ROWID or INTEGER PRIMARY KEY column is not explicitly given a value, then it will be filled automatically with an unused integer
# interestingly, int(11) PRIMARY KEY does not work for auto-increment, so for example you cannot insert into dnd_spellschool
# http://www.sqlabs.com/blog/2010/12/sqlite-and-unique-rowid-something-you-really-need-to-know/
# From the official documentation: "Rowids can change at any time and without notice. If you need to depend on your rowid, make an INTEGER PRIMARY KEY, then it is guaranteed not to change. The VACUUM command may change the ROWIDs of entries in any tables that do not have an explicit INTEGER PRIMARY KEY."

def read_xls(XLSfilepath="Monster Compendium.xls"):
  book = xlrd.open_workbook(XLSfilepath)
  print(XLSfilepath, 'has', book.nsheets, 'sheets')
  print('The sheet names are', book.sheet_names() )
  alphabetical = book.sheet_by_index(0)
  templates = book.sheet_by_index(1)
  ODE = book.sheet_by_index(3)
  #print(ODE.row_values(0) )
  #print(alphabetical.row_values(0) )
  assert ODE.row_values(0)[:33] == alphabetical.row_values(0)[:33]
  # BUT SLAs are given in the SLA column in ODE and not in alphabetical
  return alphabetical,ODE

def create_database(XLSfilepath="Monster Compendium.xls", DBpath='dnd.sqlite'):
  '''The original dnd_monster has only 29 monsters and has such design flaws as the default for attack being greatsword, so start from scratch.
  '''
  monsterOnlyDB = 'dnd_monsters.sqlite'
  if os.path.exists(monsterOnlyDB):
    os.remove(monsterOnlyDB)
  shutil.copyfile(DBpath, monsterOnlyDB)
  print('creating file', monsterOnlyDB)
  alphabetical,ODE = read_xls(XLSfilepath)
  #ipdb.set_trace()
  #print('maxlen among names =', max([str(row[0]) for row in alphabetical.get_rows()], key=len) )
  conn = sqlite3.connect(monsterOnlyDB)
  curs = conn.cursor()
  curs.execute('''CREATE TABLE monster_fly_speed (
  monster_id INTEGER NOT NULL,
  in_feet tinyint(3) NOT NULL,
  FOREIGN KEY(monster_id) REFERENCES dnd_monster(id)
  );''')

  curs.execute('''CREATE TEMPORARY TABLE types_backup (id int, name varchar(32), slug varchar(32) );''')
  curs.execute('''INSERT INTO types_backup SELECT id, name, slug FROM dnd_monstertype;''')
  curs.execute('''DROP TABLE dnd_monstertype;''')
  curs.execute('''CREATE TABLE dnd_monstertype (
  id INTEGER PRIMARY KEY NOT NULL,
  name varchar(32) NOT NULL,
  slug varchar(32) NOT NULL
  );''')
  curs.execute('''INSERT INTO dnd_monstertype SELECT id, name, slug FROM types_backup;''')
  curs.execute('''DROP TABLE types_backup;''')
  curs.execute('''INSERT INTO dnd_monstertype (name,slug) VALUES (?,?);''', ('Animal','animal') )
  curs.execute('''CREATE TEMPORARY TABLE subtypes_backup (id int, name varchar(32), slug varchar(32) );''')
  curs.execute('''INSERT INTO subtypes_backup SELECT id, name, slug FROM dnd_monstersubtype;''')
  curs.execute('''DROP TABLE dnd_monstersubtype;''')
  curs.execute('''CREATE TABLE dnd_monstersubtype (
  id INTEGER PRIMARY KEY NOT NULL,
  name varchar(32) NOT NULL,
  slug varchar(32) NOT NULL
  );''')
  curs.execute('''INSERT INTO dnd_monstersubtype SELECT id, name, slug FROM subtypes_backup;''')
  curs.execute('''DROP TABLE subtypes_backup;''')
  curs.executemany('''INSERT INTO dnd_monstersubtype (name,slug) VALUES (?,?);''', [(name, name.lower() ) for name in (
    'Aquatic','Augmented','Living Construct','Cyborg',
    'Catfolk','Tayfolk','Mongrelfolk','Dwarf','Elf','Goblinoid','Gnoll','Gnome','Kenku','Human','Orc','Skulk','Maenad','Xeph','Darfellan','Hadozee',
    'Reptilian','Dragonblood','Psionic','Incarnum','Force','Void','Shapechanger',
    'Spirit','Dream','Tasloi','Swarm','Mob','Symbiont','Wretch')])
  
  curs.execute('''DROP TABLE dnd_racesize;''')
  curs.execute('''CREATE TABLE dnd_racesize (
  id INTEGER PRIMARY KEY NOT NULL,
  name char(11) NOT NULL
  );''') # 11 in case what to say Medium-size
  curs.execute('''INSERT INTO dnd_racesize(name) VALUES ("Fine"), ("Diminutive"), ("Tiny"), ("Small"), ("Medium"), ("Large"), ("Huge"), ("Gargantuan"), ("Colossal");''')
  """ need to not have parentheses at top level:
  sqlite> insert into blanh values (3, 4, 5);
  Error: table blanh has 1 columns but 3 values were supplied
  sqlite> insert into blanh values ( (3), (4), (5) );
  Error: table blanh has 1 columns but 3 values were supplied
  sqlite> insert into blanh values (3), (4), (5);
  sqlite> insert into blanh values 3, 4, 5;
  Error: near "3": syntax error
  """

  curs.execute('''CREATE TABLE dnd_law_chaos (
  id tinyint(1) PRIMARY KEY NOT NULL,
  description CHAR(7) NOT NULL
  );''')
  #for pair in [(1, "Lawful"), (-1, "Chaotic"), (0, "Neutral")]:
  curs.execute('''INSERT INTO dnd_law_chaos (id,description) VALUES (?,?), (?,?), (?,?);''',
               (1, "Lawful", -1, "Chaotic", 0, "Neutral") )
  curs.execute('''CREATE TABLE dnd_special_ability (
  id INTEGER PRIMARY KEY NOT NULL,
  special_attack bool NOT NULL DEFAULT 0,
  name varchar(64) NOT NULL,
  type nchar(1) DEFAULT NULL,
  description longtext DEFAULT NULL
  );''')
  # simplest to use X for Ex, U for Su, P for Sp
  curs.execute('''INSERT INTO dnd_special_ability (name, description) VALUES (?, ?)''',
               ('Cold Immunity', "A creature with cold immunity never takes cold damage. It has vulnerability to fire, which means it takes half again as much (+50%) damage as normal from fire, regardless of whether a saving throw is allowed, or if the save is a success or failure.") )
  curs.execute('''INSERT INTO dnd_special_ability (name, type, description) VALUES (?, ?, ?)''',
               ('Evasion', 'X', "If subjected to an attack that allows a Reflex save for half damage, a character with evasion takes no damage on a successful save. As with a Reflex save for any creature, a character must have room to move in order to evade. A bound character or one squeezing through an area cannot use evasion. As with a Reflex save for any creature, evasion is a reflexive ability. The character need not know that the attack is coming to use evasion.") )
  #curs.execute('''INSERT INTO dnd_rulebook (id, dnd_edition_id, name, abbr, description, year, official_url, slug, image, published) VALUES (116, 7, "Monster Manual 2", "MM2", "", 1983, "", "monster-manual-ii", NULL, NULL);''')
  # see what it actually is with select * from dnd_rulebook where id=45;
  maxNameLen = len('Olhydra (Princess of Evil Water Creatures, Princess of Watery Evil, Mistress of the Black Tide)')
  #curs.execute('''DROP TABLE dnd_monsters;''')
  curs.execute('''DROP TABLE dnd_monster;''')
  curs.execute('''CREATE TABLE dnd_monster (
  id INTEGER PRIMARY KEY NOT NULL,
  rulebook_id int(11) DEFAULT NULL,
  name varchar({}) NOT NULL,
  size_id tinyint(1) NOT NULL,
  type_id tinyint(2) NOT NULL,
  hit_dice tinyint(2) NOT NULL,
  natural_armor_bonus tinyint(2) DEFAULT NULL,
  strength tinyint(2) DEFAULT NULL,
  dexterity tinyint(2) DEFAULT NULL,
  constitution tinyint(2) DEFAULT NULL,
  intelligence tinyint(2) DEFAULT NULL,
  wisdom tinyint(2) NOT NULL,
  charisma tinyint(2) NOT NULL,
  challenge_rating tinyint(2) NOT NULL,
  law_chaos_id tinyint(1) NOT NULL,
  level_adjustment tinyint(2) DEFAULT NULL,
FOREIGN KEY(rulebook_id) REFERENCES dnd_rulebook(id),
FOREIGN KEY(size_id) REFERENCES dnd_racesize(id),
FOREIGN KEY(law_chaos_id) REFERENCES dnd_law_chaos(id)
 );'''.format(maxNameLen) )
  # rulebook_id should eventually be NOT NULL,
  # but will need to add the monster books to dnd_rulebook,
  # which requires dnd_edition_id and stuff
  curs.execute('''CREATE TABLE monster_subtype (
  subtype_id INTEGER NOT NULL,
  monster_id INTEGER NOT NULL,
  FOREIGN KEY(monster_id) REFERENCES dnd_monster(id),
  FOREIGN KEY(subtype_id) REFERENCES dnd_monster(id)
  );''')
  curs.execute('''CREATE TABLE monster_special_ability (
  monster_id INTEGER NOT NULL,
  special_ability_id INTEGER NOT NULL,
FOREIGN KEY(monster_id) REFERENCES dnd_monster(id),
FOREIGN KEY(special_ability_id) REFERENCES dnd_special_ability(id)
  );''')
  curs.execute('''CREATE TABLE monster_spell_like_ability (
  monster_id INTEGER NOT NULL,
  spell_id INTEGER NOT NULL,
  caster_level tinyint(2) NOT NULL,
  caster_level_scales_with_HD bool NOT NULL,
  uses_per_day tinyint(1),
  parenthetical VARCHAR(32) DEFAULT NULL,
FOREIGN KEY(monster_id) REFERENCES dnd_monster(id),
FOREIGN KEY(spell_id) REFERENCES dnd_spell(id)
  );''')
  # It's rare, but some monsters do have SLAs of different caster levels.
  insert_psionic_powers(curs)
  # I'm guessing dropwhile has no overhead after failing
  for i,row in itertools.dropwhile(lambda p: p[0]==0,
               enumerate(ODE.get_rows() ) ):
    #if i < 4300: continue
    if i % 1000 == 0: print('processing {}th row:'.format(i), row) # since row 0 was the headings, this really is the ith row
    monster = Monster(row)
    monster.insert_into(curs)
    #if i > 8000: break
  conn.commit()
  conn.close()
  
# sqlite> select * from dnd_monsters INNER JOIN dnd_monstertype on dnd_monsters.type_id=dnd_monstertype.id;

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Incorporate an XLS file of monster data into a SQLite database.')
  parser.add_argument('XLSpath', metavar='XLS table',
                      nargs='?', default="Monster Compendium.xls",
                      help='path to the XLS table')
  parser.add_argument('DBpath', metavar='underlying database location',
                      nargs='?', default='dnd.sqlite',
                      help='path to the SQLite database')
  args = parser.parse_args()
  if not os.path.exists(args.XLSpath):
    raise OSError("The XLS table to translate was not found at {}; try python monsters.py --help for usage.".format(args.XLSpath) )
  if not os.path.exists(args.DBpath):
    raise OSError("The underlying database was not found at {}; try python monsters.py --help for usage.".format(args.DBpath) )
  profile = cProfile.Profile()
  profile.enable()
  create_database(args.XLSpath, DBpath=args.DBpath)
  profile.disable()
  with open('cProfile.txt', 'w') as statsFile:
      stats = pstats.Stats(profile, stream=statsFile)
      stats.strip_dirs().sort_stats('tottime').print_stats()
  

