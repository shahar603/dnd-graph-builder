 Prompt for LLM: D&D Campaign Dataset Creation & Network Graph - Legends of Allonanora
Objective: To collaboratively create a structured and categorized dataset detailing entities (lore, places, people, items, events, cities, etc.) and their relationships within the Dungeons & Dragons campaign "Legends of Allonanora." This dataset will serve as the primary source for later generating a comprehensive relation network graph. The dataset should categorize entities by session appearance and their position in the campaign timeline, and be structured for easy conversion into a graph format.
Campaign Context:
Campaign Name: Legends of Allonanora
World Setting: The continent of Allonanora.
Historical Context: This world has a rich history, with three prior campaigns having taken place:
The First Age (Placeholder Name): Completed campaign. Characters and events from this era are ancient history or legend.
The Second Age (Placeholder Name): Incomplete campaign. Characters and events may be from more recent history, potentially known by older NPCs.
Age 2.5 (Placeholder Name): A completed one-shot campaign. Events and characters might be known, perhaps as recent notable occurrences.
Relevance of Past Campaigns: Characters and major events from these previous campaigns are relevant to the current "Legends of Allonanora" storyline. They might reappear, be referenced in texts, or exist as legendary figures. For current player characters (PCs), much of this past information may be obscured by time, myth, or incomplete knowledge. Please factor this nuance into the dataset.
Input Data:
I will provide you with the following types of information:
DM's World-Building Notes: Descriptions of locations, historical events, key items, non-player characters (NPCs), deities, factions, and overarching lore.
Player Session Notes: These may include:
In-character journal entries reflecting a PC's perspective and knowledge.
General summaries of session events, discoveries, and interactions.
Player theories and observations (distinguish these from established facts if possible).
Prologue & Adventure Modules: Narrative content setting up the current campaign and specific adventures.
Task Breakdown & Process:
Initial Analysis & Clarification (Your First Task):
Acknowledge your understanding of this entire request.
Once I provide the initial batch of information (starting with the "Legends of Allonanora" prologue), your primary goal is to analyze it thoroughly.
Ask me targeted questions to clarify ambiguities, identify potential connections, and ensure you understand the entities, their attributes, and their relationships.
Specifically, I need you to help identify:
Key Entities: What are the most important people (PCs, NPCs), places (cities, dungeons, geographical features), items, organizations, events, and distinct pieces of lore?
Entity Attributes: For each entity, what are its defining characteristics, properties, or key details?
Potential Relationships: How might these entities be connected? (e.g., "Is [NPC A] a member of [Organization X]?" or "Did [Event Y] take place in [City Z]?").
Information Gaps: What crucial information seems to be missing that would help establish a clearer understanding, categorization, or relationship?
Categorization Details: How should entities be categorized by session (e.g., "Introduced in Session 3," "Relevant to Prologue") or timeline period (e.g., "First Age Myth," "Current Era - Legends of Allonanora," "Age 2.5 Event")?
Distinguishing Knowledge: Help me differentiate between:
Objective facts of the world.
Information known by specific NPCs.
Information known or perceived by the current PCs.
Legends or rumored information.
Dataset Creation & Categorization (Iterative Process):
After the initial analysis and Q&A, and as I provide more information, you will help me construct a structured dataset.
Desired Output Format for the Dataset: Please represent the data as a collection of records (e.g., a list of JSON-like objects). Each record should detail an entity and its associated information. This format is intended to be directly parsable for network graph generation.
Key Information to Capture per Entity Record:
EntityID: A unique identifier you assign (e.g., "CHAR_001", "PLACE_001", "EVENT_001"). This will serve as the node ID in the graph.
Name: The common name of the entity.
Type: The category of the entity (e.g., Character, NPC, PC, Place, City, Region, Item, Artifact, Event, Lore, Organization, Faction). This can be a node property.
Description: A brief summary of the entity and its significance. (Node property)
TimelineCategory: The historical or campaign era the entity belongs to (e.g., "Prologue - Legends of Allonanora," "First Age Myth," "Second Age History," "Age 2.5 Event," "Current Era - Legends of Allonanora," "Pre-Campaign Lore"). (Node property)
SessionAppearance: Information about when/where in the campaign sessions this entity was introduced or is relevant (e.g., "Session 1," "Sessions 3-5," "DM Notes - Pre-Campaign," "Prologue Text"). (Node property)
Relations: A list of relationship objects, each defining an outgoing edge from the current entity. Each relationship object specifies:
RelatedEntityID: The EntityID of the target node for this edge.
RelationshipType: The label or type of the edge (e.g., "allied with," "enemy of," "located in," "parent of," "created by," "found during," "knows about," "member of," "witnessed"). This will be the edge label.
Attributes: (Optional) A flexible field for other key details specific to the relationship itself (e.g., for a "knows about" relationship: {"Certainty": "High", "Source": "Direct Observation"}; for an "allied with" relationship: {"Strength": "Strong", "Duration": "Since Childhood"}). These will be edge properties.
SourceNotes: Brief reference to where this information originated (e.g., "DM world notes," "Vince's journal S2," "Prologue - Paragraph 3"). (Node property)
KnowledgeScope: Indication of who knows this information and its veracity (e.g., "Objective Fact," "PC Knowledge (Vince)," "NPC Knowledge (Old Man Hemlock)," "Common Rumor," "Obscure Legend"). (Node property)
Attributes: (Optional) A flexible field for other key details specific to the entity type, which will serve as additional node properties (e.g., for a Character: {"Class": "Wizard", "Race": "Elf"}; for an Item: {"MagicalProperties": "Grants invisibility", "Charges": 3}).
We will build this dataset iteratively. After each significant batch of new information and our Q&A, you will propose new entries or updates to existing entries in the dataset.
Relation Network Graph Generation (Subsequent Goal):
The primary goal of this phase is to create the comprehensive, categorized dataset.
Once the dataset is sufficiently detailed and accurate, we will then use it as the foundation to generate a relation network graph. The dataset structure is designed for this: each entity record will become a node (using its EntityID as the unique node identifier and other fields like Name, Type, Description, etc., as node properties). Each item in an entity's Relations list will define an edge (from the current entity's EntityID to the RelatedEntityID, with RelationshipType as the edge label and any specified Attributes within the relation object as edge properties). You may be asked later to propose a graph structure based on the final dataset.
Information about the "Legends of Allonanora" Player Group (For Context - Not for direct inclusion in the dataset as primary entities unless an in-game element refers to them):
Game Master (DM): Roey
Current Player Characters (PCs):
Vince: Wizard (Played by Nadav)
Leonard: Artificer (Played by Aviv)
Granite Stonebreaker: Barbarian (Played by Tomer)
Eleca: Warlock (Played by Ilan)
Former Player Character:
Stella: Druid (Played by Nicole - not currently playing)
Confirmation Request:
Please confirm your understanding of these updated instructions, particularly the focus on creating a detailed dataset first (with the specified structure for entities and their relations, including optional attributes for relations), with categorization by timeline and session, which will then be used for network graph generation. Once you confirm, I will provide the prologue for "Legends of Allonanora."
Example Dataset Entries (Illustrative):
Example Character (PC) Entry:
{
  "EntityID": "PC_VINCE_001",
  "Name": "Vince",
  "Type": "PC",
  "Description": "A studious wizard, member of the 'Legends of Allonanora' adventuring party. Played by Nadav.",
  "TimelineCategory": "Current Era - Legends of Allonanora",
  "SessionAppearance": "Session 1 - Ongoing",
  "Relations": [
    { 
      "RelatedEntityID": "PC_LEONARD_001", 
      "RelationshipType": "party member with",
      "Attributes": {"TrustLevel": "High", "SharedExperiences": ["Battle of Greenfields", "Discovery of the Sunstone"]}
    },
    { 
      "RelatedEntityID": "ITEM_ANCIENTSCROLL_001", 
      "RelationshipType": "currently researching",
      "Attributes": {"Progress": "Partial Translation", "Goal": "Uncover lost spell"}
    }
  ],
  "SourceNotes": "Player Character List; Session 1 Notes; Vince's Journal Entry S3",
  "KnowledgeScope": "Objective Fact (Player Roster & Actions); PC Knowledge (Vince - research details)",
  "Attributes": { "Class": "Wizard", "Player": "Nadav", "Specialization": "Abjuration" }
}


Example Event Entry:
{
  "EntityID": "EVENT_SUNDERING_001",
  "Name": "The Sundering of Eldoria",
  "Type": "Event",
  "Description": "A cataclysmic magical event from the First Age that shattered the continent of Eldoria and reshaped local geography.",
  "TimelineCategory": "First Age Myth",
  "SessionAppearance": "Lore Drop - Session 4 (Ancient Text Discovery)",
  "Relations": [
    { 
      "RelatedEntityID": "PLACE_RUINSELDORIA_001", 
      "RelationshipType": "caused destruction of",
      "Attributes": {"Severity": "Total Annihilation", "Method": "Uncontrolled Arcane Surge"}
    },
    { 
      "RelatedEntityID": "LORE_PROPHECYOFRETURN_001", 
      "RelationshipType": "is a key component of"
    }
  ],
  "SourceNotes": "DM world notes - Ancient History; Session 4 Player Handout (Tattered Scroll)",
  "KnowledgeScope": "Legend/Myth (partially known by PCs via ancient texts, full details known to DM)",
  "Attributes": { "Magnitude": "Continental Scale", "Nature": "Magical Cataclysm", "Aftermath": "Creation of the Shattered Isles" }
}


Example Place Entry:
{
  "EntityID": "PLACE_RUINSELDORIA_001",
  "Name": "Ruins of Eldoria",
  "Type": "Place (Ruined City)",
  "Description": "The shattered remnants of an ancient city, now a dangerous ruin, a direct consequence of The Sundering of Eldoria.",
  "TimelineCategory": "First Age Myth (as a city) / Current Era - Legends of Allonanora (as ruins)",
  "SessionAppearance": "Mentioned in Session 4 Lore; Rumored location for ITEM_ANCIENTSCROLL_001 (Session 5 discussion)",
  "Relations": [
    { 
      "RelatedEntityID": "EVENT_SUNDERING_001", 
      "RelationshipType": "destroyed by" 
    },
    { 
      "RelatedEntityID": "ITEM_ANCIENTSCROLL_001", 
      "RelationshipType": "rumored location of",
      "Attributes": {"RumorSource": "Old Fisherman's Tale", "Reliability": "Low"}
    }
  ],
  "SourceNotes": "DM world notes - Locations; Player theories from Session 5",
  "KnowledgeScope": "Known location (existence as ruins), details of former city are legend. Rumors about scroll are PC knowledge.",
  "Attributes": { "CurrentState": "Ruined, Dangerous, Unexplored", "FormerCivilization": "Eldorian Empire (First Age)", "DominantCreatures": "Spectral Guardians, Shadow Beasts" }
}
