eam_prompts = """
    Given the following SQL tables, please write the SQL query based on the schema provided and the question.
    Please provide the query as required by SQL Server.
    Provide only the SQL query.

    Tables:
    assets
    control_measures
    hazards
    location_hazard
    locations
    
    How are the tables related to each other?
    control_measures table has a foreign key relationship with the location_hazard table 
    through the location_hazard_id field.
    location_hazard table has a foreign key relationship with the locations table 
    through the location_name field.
    location_hazard table has a foreign key relationship with the hazards table 
    through the hazard_id field

    Schema:

    CREATE TABLE IF NOT EXISTS assets (
    asset_id TEXT PRIMARY KEY,
    asset_name TEXT NOT NULL,
    asset_type TEXT,
    manufacturer TEXT,
    model_number TEXT, installation_date DATE,
    last_maintenance_date DATE,
    location_name TEXT,
    status TEXT,
    description TEXT
);
CREATE TABLE IF NOT EXISTS control_measures (
    control_measure_id VARCHAR PRIMARY KEY,
    location_hazard_id VARCHAR,
    measure_description VARCHAR,
    implementation_date DATE,
    status VARCHAR,
    responsible_person VARCHAR,
    review_frequency VARCHAR,
    last_review_date DATE,
    effectiveness_rating VARCHAR
);
CREATE TABLE IF NOT EXISTS hazards (
    hazard_id TEXT PRIMARY KEY,
    hazard_name TEXT NOT NULL,
    hazard_category TEXT,
    description TEXT,
    severity_level TEXT,
    location_name TEXT
);
CREATE TABLE IF NOT EXISTS location_hazard (
    location_hazard_id VARCHAR PRIMARY KEY,
    location_name VARCHAR,
    hazard_id VARCHAR,
    status VARCHAR,
    identified_date DATE,
    last_review_date DATE,
    risk_level VARCHAR,
    reviewed_by VARCHAR
);
CREATE TABLE IF NOT EXISTS locations (
    location_name VARCHAR,
    description VARCHAR,
    latitude DOUBLE,
    longitude DOUBLE,
    address VARCHAR
);
CREATE TABLE IF NOT EXISTS work_orders (
    work_order_id VARCHAR(500) PRIMARY KEY,
    description TEXT,
    location_name TEXT,
    asset_id VARCHAR(500),
    status TEXT,
    scheduled_start_timestamp TIMESTAMP,
    scheduled_finish_timestamp TIMESTAMP,
    owner_name TEXT,
    priority INTEGER
);
"""