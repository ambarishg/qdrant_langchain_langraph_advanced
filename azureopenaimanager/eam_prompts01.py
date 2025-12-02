eam_prompts_part_1 = """
    Given the following SQL tables,
    Tables:
    assets
    control_measures
    hazards
    location_hazard
    locations

    get the tables required for the query. Provide only the 
    names of the tables and no extra information.

    Example of the response is Table1, Table2
    
    
    How are the tables related to each other?
    control_measures table has a foreign key relationship with the location_hazard table 
    through the location_hazard_id field.
    location_hazard table has a foreign key relationship with the locations table 
    through the location_name field.
    location_hazard table has a foreign key relationship with the hazards table 
    through the hazard_id field


    """