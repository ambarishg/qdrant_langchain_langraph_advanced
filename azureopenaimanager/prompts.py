question = """
    Given the following SQL tables, please write the SQL query based on the schema provided and the question.
    Please provide the query as required by SQL Server.
    Provide only the SQL query.
    Make the MeasurementType filter value in CAPS.
    
   
    CREATE TABLE IF NOT EXISTS measurements (
    Organization VARCHAR,
    Location VARCHAR,
    AssetGroup VARCHAR,
    Asset VARCHAR,
    MeasurementType VARCHAR,
    Value DOUBLE,
    Date DATETIME
);   
"""

max_tokens = 1000
temperature = 0.0
top_p = 0.9
frequency_penalty = 0
presence_penalty = 0.1