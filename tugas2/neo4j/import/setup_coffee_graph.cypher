// 1. CONSTRAINTS (to ensure uniqueness)

CREATE CONSTRAINT IF NOT EXISTS
FOR (c:Coffee)
REQUIRE c.code IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS
FOR (b:Base)
REQUIRE b.code IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS
FOR (m:MilkType)
REQUIRE m.code IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS
FOR (a:Additive)
REQUIRE a.code IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS
FOR (p:PreparationMethod)
REQUIRE p.code IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS
FOR (s:ServingStyle)
REQUIRE s.code IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS
FOR (o:Origin)
REQUIRE o.code IS UNIQUE;


// 2. CATEGORY NODES (Base, Milk, Additive, Preparation, Serving, Origin)

UNWIND [
  {code: "espresso",       name: "Espresso"},
  {code: "brewed_coffee",  name: "Brewed Coffee"}
] AS row
MERGE (b:Base {code: row.code})
SET b.name = row.name;

UNWIND [
  {code: "none",               name: "No Milk"},
  {code: "steamed_milk",       name: "Steamed Milk"},
  {code: "foamed_milk",        name: "Foamed Milk"},
  {code: "steamed_and_foamed", name: "Steamed + Foamed Milk"},
  {code: "microfoam",          name: "Microfoam Milk"},
  {code: "cold_milk",          name: "Cold Milk"}
] AS row
MERGE (m:MilkType {code: row.code})
SET m.name = row.name;

UNWIND [
  {code: "none",       name: "No Additive"},
  {code: "hot_water",  name: "Hot Hot Water"},
  {code: "sugar",      name: "Sugar"},
  {code: "chocolate",  name: "Chocolate"}
] AS row
MERGE (a:Additive {code: row.code})
SET a.name = row.name;

UNWIND [
  {code: "pressure", name: "Pressure Extraction"},
  {code: "boiled",   name: "Boiled"},
  {code: "diluted",  name: "Diluted"},
  {code: "combined", name: "Combined Method"}
] AS row
MERGE (p:PreparationMethod {code: row.code})
SET p.name = row.name;

UNWIND [
  {code: "small_cup",  name: "Small Cup"},
  {code: "tall_glass", name: "Tall Glass"},
  {code: "large_cup",  name: "Large Cup"},
  {code: "demitasse",  name: "Demitasse"},
  {code: "unfiltered", name: "Unfiltered Cup"},
  {code: "cup",        name: "Cup"}
] AS row
MERGE (s:ServingStyle {code: row.code})
SET s.name = row.name;

UNWIND [
  {code: "italy",                 name: "Italy"},
  {code: "portugal",              name: "Portugal"},
  {code: "indonesia",             name: "Indonesia"},
  {code: "greece",                name: "Greece"},
  {code: "australia_new_zealand", name: "Australia & New Zealand"}
] AS row
MERGE (o:Origin {code: row.code})
SET o.name = row.name;


// 3. COFFEE NODES + RELATIONSHIPS

UNWIND [
  {code:"espresso",        name:"Espresso",        base:"espresso",       milk:"none",               additive:"hot_water", preparation:"pressure", serving:"small_cup",  origin:"italy"},
  {code:"bica",            name:"Bica",            base:"espresso",       milk:"none",               additive:"hot_water", preparation:"pressure",  serving:"demitasse", origin:"portugal"},
  {code:"americano",       name:"Americano",       base:"espresso",       milk:"none",               additive:"hot_water", preparation:"diluted",   serving:"large_cup", origin:"italy"},
  {code:"latte",           name:"Latte",           base:"espresso",       milk:"steamed_milk",       additive:"none",      preparation:"combined",  serving:"tall_glass",origin:"italy"},
  {code:"caffe_macchiato", name:"Caffè Macchiato", base:"espresso",       milk:"foamed_milk",        additive:"none",      preparation:"combined",  serving:"small_cup", origin:"italy"},
  {code:"cappuccino",      name:"Cappuccino",      base:"espresso",       milk:"steamed_and_foamed", additive:"none",      preparation:"combined",  serving:"cup",       origin:"italy"},
  {code:"flat_white",      name:"Flat White",      base:"espresso",       milk:"microfoam",          additive:"none",      preparation:"combined",  serving:"small_cup", origin:"australia_new_zealand"},
  {code:"latte_macchiato", name:"Latte Macchiato", base:"espresso",       milk:"steamed_milk",       additive:"none",      preparation:"combined",  serving:"tall_glass",origin:"italy"},
  {code:"kopi_tubruk",     name:"Kopi Tubruk",     base:"brewed_coffee",  milk:"none",               additive:"sugar",     preparation:"boiled",    serving:"unfiltered",origin:"indonesia"},
  {code:"greek_coffee",    name:"Greek Coffee",    base:"brewed_coffee",  milk:"none",               additive:"sugar",     preparation:"boiled",    serving:"unfiltered",origin:"greece"},
  {code:"cafe_mocha",      name:"Café Mocha",      base:"espresso",       milk:"steamed_milk",       additive:"chocolate", preparation:"combined",  serving:"cup",       origin:"italy"}
] AS row

// Create coffee node
MERGE (c:Coffee {code: row.code})
SET c.name = row.name

// Base
WITH c, row
MATCH (b:Base {code: row.base})
MERGE (c)-[:HAS_BASE]->(b)

// Milk
WITH c, row
MATCH (m:MilkType {code: row.milk})
MERGE (c)-[:HAS_MILK]->(m)

// Additive
WITH c, row
MATCH (a:Additive {code: row.additive})
MERGE (c)-[:HAS_ADDITIVE]->(a)

// Preparation
WITH c, row
MATCH (p:PreparationMethod {code: row.preparation})
MERGE (c)-[:USES_PREPARATION]->(p)

// Serving
WITH c, row
MATCH (s:ServingStyle {code: row.serving})
MERGE (c)-[:SERVED_IN]->(s)

// Origin
WITH c, row
MATCH (o:Origin {code: row.origin})
MERGE (c)-[:ORIGINATES_FROM]->(o);