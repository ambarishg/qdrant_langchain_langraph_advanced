eam_prompts_header = """
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

    work orders table specifics -
    Make the status filter in the work_orders table in CamelCase.
    The valid values for status are: New, In Progress, Completed, On Hold, Cancelled, Approved
    Make the owner_name filter a LIKE filter.
    Make the description filter case insensitive.

    Schema:

 """