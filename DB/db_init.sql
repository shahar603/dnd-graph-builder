-- Ensure Foreign Key support is enabled (run this command before executing the schema)
PRAGMA foreign_keys = ON;

CREATE TABLE Character (
  character_id INTEGER PRIMARY KEY AUTOINCREMENT,
  character_name TEXT,
  character_description TEXT,
  character_type TEXT CHECK (character_type IN ('DEITY', 'MONSTER', 'NPC', 'PC', 'HISTORICAL_PC')),
  alignment TEXT CHECK (alignment IN ('GOOD', 'BAD', 'LAWFUL', 'CHAOTIC', 'GOOD_LAWFUL', 'BAD_LAWFUL', 'GOOD_CHAOTIC', 'BAD_CHAOTIC', 'NEUTRAL', 'UNKNOWN')),
  access_level TEXT DEFAULT 'ALL' CHECK (access_level IN ('ALL', 'DM'))
);

CREATE TABLE Player (
  player_id INTEGER PRIMARY KEY AUTOINCREMENT,
  player_name TEXT,
  access_level TEXT DEFAULT 'ALL' CHECK (access_level IN ('ALL', 'DM'))
);

CREATE TABLE Player_Characters (
  character_id INTEGER UNIQUE,
  player_id INTEGER,
  access_level TEXT DEFAULT 'ALL' CHECK (access_level IN ('ALL', 'DM')),
  PRIMARY KEY (character_id, player_id),
  FOREIGN KEY (character_id) REFERENCES Character (character_id),
  FOREIGN KEY (player_id) REFERENCES Player (player_id)
);

CREATE TABLE Item (
  item_id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_name TEXT,
  item_description TEXT,
  value_in_gold INTEGER,
  rarity TEXT CHECK (rarity IN ('COMMON', 'UNCOMMON', 'RARE', 'VERY_RARE', 'LEGENDARY')),
  is_magical INTEGER, -- Using INTEGER for boolean (0 for false, 1 for true)
  creator_id INTEGER,
  FOREIGN KEY (creator_id) REFERENCES Character (character_id)
);

CREATE TABLE Location (
  location_id INTEGER PRIMARY KEY AUTOINCREMENT,
  location_name TEXT,
  location_description TEXT,
  region TEXT,
  climate TEXT,
  ruler INTEGER,
  FOREIGN KEY (ruler) REFERENCES Character (character_id)
);

CREATE TABLE Event (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_description TEXT,
  event_type TEXT CHECK (event_type IN ('GENERAL', 'HISTORICAL', 'ENCOUNTER')),
  era TEXT
);

CREATE TABLE Event_Participants (
  character_id INTEGER,
  event_id INTEGER,
  PRIMARY KEY (character_id, event_id),
  FOREIGN KEY (character_id) REFERENCES Character (character_id),
  FOREIGN KEY (event_id) REFERENCES Event (event_id)
);

CREATE TABLE Session (
  session_id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_description TEXT
);

CREATE TABLE GenericRelation (
  relation_id INTEGER PRIMARY KEY AUTOINCREMENT,
  Table1Name TEXT NOT NULL CHECK (Table1Name IN ('CHARACTER', 'ITEM', 'LOCATION', 'EVENT')),
  Table1ID INTEGER NOT NULL,
  Table2Name TEXT NOT NULL CHECK (Table2Name IN ('CHARACTER', 'ITEM', 'LOCATION', 'EVENT')),
  Table2ID INTEGER NOT NULL,
  relation_description TEXT,
  relation_appearance INTEGER,
  FOREIGN KEY (relation_appearance) REFERENCES Session (session_id)
);