question = """
    Given the following SQL tables, please write the SQL query based on the schema provided and the question.
    Please provide the query as required by SQL Server.
    Provide only the SQL query.
    Make the MeasurementType filter value in CAPS.
    Make the status filter in the work_orders table in CamelCase.
    The valid values for status are: New, In Progress, Completed, On Hold, Cancelled, Approved
    Make the owner_name filter a LIKE filter.
   
    CREATE TABLE IF NOT EXISTS measurements (
    Organization VARCHAR,
    Location VARCHAR,
    AssetGroup VARCHAR,
    Asset VARCHAR,
    MeasurementType VARCHAR,
    Value DOUBLE,
    Date DATETIME
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

max_tokens = 1000
temperature = 0.0
top_p = 0.9
frequency_penalty = 0
presence_penalty = 0.1