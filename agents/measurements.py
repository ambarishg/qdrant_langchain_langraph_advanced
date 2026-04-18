from agents.graph_state import GraphState
from agents.generate_sql import get_sql_query
from azureopenaimanager.prompts import question


NO_RECORDS_MESSAGE = "No records were found for the requested measurements."


def get_database_results(state: GraphState) -> dict:
    """Extract and return measurements from the state."""

    print("---GET MEASUREMENTS---")
    question2 = state["question"]
    sql_query = None
    try:
        context = question
        question2, sql_query = get_sql_query(state,context)

        if sql_query:        
            from db.duckdb.duckdbhelper import DuckDBDatabaseHelper
            duckdb_helper = DuckDBDatabaseHelper('data/test_duckdb.db')
            duckdb_helper.connect()
            results, column_names = duckdb_helper.fetch_all(sql_query)
            duckdb_helper.close_connection()

            if results is not None and len(results) > 0:
                import pandas as pd
                df = pd.DataFrame(results)
                df.columns = column_names
                dict_df = df.to_dict(orient='records')
                return {"question": question2, "generation": dict_df, "documents": str(sql_query), "datasource": "measurements"}
            else:
                return {"question": question2, "generation": NO_RECORDS_MESSAGE, "documents": str(sql_query), "datasource": "measurements"}
        else:
                return {"question": question2, "generation": NO_RECORDS_MESSAGE, "documents": str(sql_query), "datasource": "measurements"}
    except Exception as e:
        print(f"Error in get_measurements: {e}")
        return {"question": question2, "generation": NO_RECORDS_MESSAGE, "documents": str(sql_query), "datasource": "measurements"}
