CREATE TABLE `Character` (
  `character_id` long PRIMARY KEY AUTO_INCREMENT,
  `character_name` varchar(255),
  `character_description` varchar(255),
  `character_type` ENUM ('DEITY', 'MONSTER', 'NPC', 'PC', 'HISTORICAL_PC'),
  `alignment` ENUM ('GOOD', 'BAD', 'LAWFUL', 'CHAOTIC', 'GOOD_LAWFUL', 'BAD_LAWFUL', 'GOOD_CHAOTIC', 'BAD_CHAOTIC', 'NEUTRAL', 'UNKNOWN'),
  `access_level` ENUM ('ALL', 'DM') DEFAULT 'ALL'
);

CREATE TABLE `Player` (
  `player_id` long PRIMARY KEY AUTO_INCREMENT,
  `player_name` varchar(255),
  `access_level` ENUM ('ALL', 'DM') DEFAULT 'ALL'
);

CREATE TABLE `Player_Characters` (
  `character_id` long UNIQUE,
  `player_id` long,
  `access_level` ENUM ('ALL', 'DM') DEFAULT 'ALL',
  PRIMARY KEY (`character_id`, `player_id`),
  FOREIGN KEY (`character_id`) REFERENCES `Character` (`character_id`),
  FOREIGN KEY (`player_id`) REFERENCES `Player` (`player_id`)
);

CREATE TABLE `Item` (
  `item_id` long PRIMARY KEY AUTO_INCREMENT,
  `item_name` varchar(255),
  `item_description` varchar(255),
  `value_in_gold` INTEGER,
  `rarity` ENUM ('COMMON', 'UNCOMMON', 'RARE', 'VERY_RARE', 'LEGENDARY'),
  `is_magical` bool,
  `creator_id` long,
  FOREIGN KEY (`creator_id`) REFERENCES `Character` (`character_id`)
);

CREATE TABLE `Location` (
  `location_id` long PRIMARY KEY AUTO_INCREMENT,
  `location_name` varchar(255),
  `location_description` varchar(255),
  `region` varchar(255),
  `climate` varchar(255),
  `ruler` long, -- Changed from 'character_id' to 'long' for clarity
  FOREIGN KEY (`ruler`) REFERENCES `Character` (`character_id`)
);

CREATE TABLE `Event` (
  `event_id` long PRIMARY KEY AUTO_INCREMENT,
  `event_description` varchar(255),
  `event_type` ENUM ('GENERAL', 'HISTORICAL', 'ENCOUNTER'),
  `era` varchar(255)
);

CREATE TABLE `Event_Participants` (
  `character_id` long,
  `event_id` long,
  PRIMARY KEY (`character_id`, `event_id`),
  FOREIGN KEY (`character_id`) REFERENCES `Character` (`character_id`),
  FOREIGN KEY (`event_id`) REFERENCES `Event` (`event_id`)
);

CREATE TABLE `Session` (
  `session_id` long PRIMARY KEY AUTO_INCREMENT,
  `session_description` varchar(255)
);

CREATE TABLE `GenericRelation` (
  `relation_id` long PRIMARY KEY AUTO_INCREMENT,
  `Table1Name` ENUM ('CHARACTER', 'ITEM', 'LOCATION', 'EVENT') NOT NULL,
  `Table1ID` long NOT NULL,
  `Table2Name` ENUM ('CHARACTER', 'ITEM', 'LOCATION', 'EVENT') NOT NULL,
  `Table2ID` long NOT NULL,
  `relation_description` VARCHAR(255), -- Added length to VARCHAR
  `relation_appearance` long,
  FOREIGN KEY (`relation_appearance`) REFERENCES `Session` (`session_id`)
);