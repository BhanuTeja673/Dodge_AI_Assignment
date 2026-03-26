import os
import google.generativeai as genai
import sqlite3
import pandas as pd

class QuerySystem:
    def __init__(self, db_conn):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            self.model = None
            
        self.db_conn = db_conn
        
        # Get schema definition using pandas to pass to AI
        self.schema_info = self._get_schema()
        
    def _get_schema(self):
        try:
            # Query the sqlite master table to get all create statements
            df = pd.read_sql_query("SELECT name, sql FROM sqlite_master WHERE type='table';", self.db_conn)
            schema_str = ""
            for _, row in df.iterrows():
                schema_str += f"{row['sql']}\n"
            return schema_str
        except Exception:
            return "No schema available."
            
    def _check_guardrails(self, query: str) -> bool:
        lower_q = query.lower()
        if any(keyword in lower_q for keyword in ['joke', 'poem', 'write a', 'who is', 'meaning of life', 'code']):
            return False
        return True

    def process_query(self, query: str) -> str:
        if not self.model:
            return "Error: GEMINI_API_KEY is not set in the environment. Please configure it to use the AI Query System."
            
        if not self._check_guardrails(query):
            return "This system is designed to answer questions related to the provided dataset only."
            
        try:
            # 1. Ask Gemini to convert NL to SQL
            sql_prompt = f"""
            You are a data assistant. Your job is to accurately translate a natural language question into a SQLite query based on the following schema.
            Schema:
            {self.schema_info}
            
            Question: {query}
            
            Return ONLY the raw SQL query, without markdown backticks or explanations.
            """
            
            result = self.model.generate_content(sql_prompt)
            sql_query = result.text.strip().replace("```sql", "").replace("```", "")
            
            # 2. Execute SQL
            df_result = pd.read_sql_query(sql_query, self.db_conn)
            data_string = df_result.to_string()
            
            # 3. Formulate natural language response
            nl_prompt = f"""
            The user asked: "{query}"
            The database returned the following data:
            {data_string}
            
            Provide a polite, natural language summary of the result based only on this data. If the data is empty or 'None', say no matching records were found.
            """
            final_res = self.model.generate_content(nl_prompt)
            return final_res.text
            
        except Exception as e:
            return f"System experienced an error processing the natural language query. It attempted a SQL lookup but failed due to: {str(e)}"
