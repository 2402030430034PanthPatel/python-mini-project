from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import streamlit as st
import os
import google.generativeai as genai
import mysql.connector

# Configure our api key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load google gemini model and provide query as response
def get_gemini_response(question,prompt):
    model=genai.GenerativeModel('gemini-pro')
    response=model.generate_content([prompt[0],question])
    return response.text

# Function to retrieve query from SQL database
def read_sql_query(sql, db_host, db_user, db_password, db_name):
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    columns_names = [col[0] for col in cur.description]
    df = pd.DataFrame(rows,columns=columns_names)
    conn.commit()
    conn.close()
    
    for row in rows:
        print(row)
    
    return df

# Define your prompt
prompt=[
  """
    You are an expert in converting English questions to SQL queries!
    The SQL database you are working with contains two tables: Hapasar and Jhansi.
    The structure of these tables is as follows:
    
   You are an expert in converting English questions to SQL queries!
The SQL database you are working with contains two tables: processed and processed1.
The structure of these tables is as follows:

Table: processed
Fields: plant, timereading, AssetName, currentgained, voltagegained, currentused, voltageused, currentgeneration, voltagegeneration, powergeneration, TargetA, positionB, manuel, auto, Kpi1, Kpi2, kpivalue, finalkpitracker, result, NetExportD.

Table: processed1
Fields: plant, timereading, AssetName, currentgained, voltagegained, currentused, voltageused, currentgeneration, voltagegeneration, powergeneration, TargetA, positionB, manuel, auto, Kpi1, Kpi2, kpivalue, finalkpitracker, result, NetExportD.

Examples of questions and their corresponding SQL queries:

- Question: How many records are there in the Hapasar Plant?
  SQL Command: SELECT COUNT(*) AS num_records FROM processed WHERE plant = 'Hapasar';

- Question: Show the unique plants in the Jhansi table.
  SQL Command: SELECT DISTINCT plant FROM processed1;

- Question: Retrieve the current generation readings for Asset 'Asset 1' from the Hapasar table.
  SQL Command: SELECT timereading, currentgeneration FROM processed WHERE AssetName = 'Asset1';

- Question: Find the average voltage generation across all assets in the Jhansi table.
  SQL Command: SELECT AVG(voltagegeneration) AS average_voltage_generation FROM processed1;

- Question: Which asset has the highest current gained in the Hapasar table?
  SQL Command: SELECT AssetName, MAX(currentgained) AS max_current_gained FROM processed;

- Question: Show the power generation readings for Asset 'Asset 2' from the Jhansi table.
  SQL Command: SELECT timereading, powergeneration FROM processed1 WHERE AssetName = 'Asset2';

- Question: Find the total number of records in the Jhansi table.
  SQL Command: SELECT COUNT(*) AS total_records FROM processed1;


Your task is to determine the best-performing plant based on the sum of result.

- To find the sum of NetExportD for each plant:
SELECT 
    CASE
        WHEN max_sum_result_jhansi > sum_result_hapasar THEN 'Jhansi'
        ELSE 'Hapasar'
    END AS jhansi_greater_than_hapasar
FROM (
    SELECT 
        MAX(sum_result_jhansi) AS max_sum_result_jhansi,
        (SELECT SUM(result) FROM processed WHERE plant = 'Hapasar') AS sum_result_hapasar
    FROM (
        SELECT SUM(result) AS sum_result_jhansi
        FROM processed1
        WHERE plant = 'Jhansi'
    ) AS jhansi_sum
) AS subquery;

You can ask me to identify the best-performing plant by querying the sum of result.

Your task is to determine the best-performing Asset based on the sum of result for specific dates.

- To find the sum of result for each Asset on a specific date:
  SQL Command for processed on 2024-01-06:
  SELECT AssetName, SUM(result) AS resultH1 FROM processed WHERE plant = 'Hapasar' AND timereading >= '2024-01-06 00:00:00' AND timereading < '2024-01-07 00:00:00' GROUP BY AssetName;
  
For example:
  If the sum of NetExportH1 for Asset1 on 2024-01-06 in Hapasar is higher than the sum of resultH1 for Asset2 on 2024-01-06 in Hapasar, then Asset 1 in Hapasar is the best-performing Asset on that date.

You can ask me to identify the best-performing Asset on specific dates by querying the sum of result.



    also the SQL code should NOT have ''' in beginning or end and sql word in output
    after generating the query remove ''' and sql word from beginning and end

    """

]


column_mapping = {col.lower(): col for col in [ "plant", "timereading", "AssetName", "currentgained", "voltagegained", "currentused", "voltageused", "currentgeneration", "voltagegeneration", "powergeneration", "TargetA", "positionB", "manuel", "auto", "Kpi1", "Kpi2", "kpivalue", "finalkpitracker", "result", "NetExportD"]}

# Streamlit App
st.set_page_config(page_title="Panth's Chatbot")
st.header("Unfold the secret's that lie in your Database")
question=st.text_input("Challenge Me Here ",key="input")
submit=st.button("Press to get a Answer")

# MySQL database configuration
db_host = '127.0.0.1'
db_user = 'root'
db_password = 'Panth2005@'
db_name = 'timestamp'

if submit:
    # Get Gemini response
    response = get_gemini_response(question, prompt)
    print(response)

    # Process the response to generate SQL query
    # Here, we'll assume the response contains the SQL query directly
    generated_sql_query = response

    # Read SQL query and fetch data
    data = read_sql_query(generated_sql_query, db_host, db_user, db_password, db_name)
    st.write(data)