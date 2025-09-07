from agents.generate_sql import *

from azureopenaimanager.eam_prompts import eam_prompts

from agents.graph_state import GraphState

def get_eam_results(state: GraphState) -> dict:
    """Extract and return measurements from the state."""

    print("---GET EAM RESULTS---")
    try:
        context = eam_prompts
        question, sql_query = get_sql_query(state, context)

        from db.duckdb.duckdbhelper import DuckDBDatabaseHelper
        duckdb_helper = DuckDBDatabaseHelper('data/eam.db')
        duckdb_helper.connect()
        results, column_names = duckdb_helper.fetch_all(sql_query)
        duckdb_helper.close_connection()

        if results is not None and len(results) > 0:
            import pandas as pd
            df = pd.DataFrame(results)
            df.columns = column_names
            dict_df = df.to_dict(orient='records')
            return {"question": question, "generation": dict_df, "documents": str(sql_query), "datasource": "EAM"}
        else:
            return {"question": question, "generation": [{'0':'No records found'}], "documents": str(sql_query)}
    except Exception as e:
        print(f"Error in get_eam_results: {e}")
        return {"question": question, "generation": [{'0':'No records found'}], "documents": str(sql_query), "datasource": "EAM"}
