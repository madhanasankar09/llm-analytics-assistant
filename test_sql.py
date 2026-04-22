from sql.nl_to_sql import generate_sql, run_sql, explain_result

query = "How many orders are delivered?"

sql_query = generate_sql(query)
print("Generated SQL:", sql_query)

df = run_sql(sql_query)
print(df.head())

explanation = explain_result(query, df)
print("Explanation:", explanation)