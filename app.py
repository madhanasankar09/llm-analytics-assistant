import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os
import importlib.util

# 🔥 FIXED MODULE LOADING (WORKS ALWAYS)

# SQL
spec_sql = importlib.util.spec_from_file_location(
    "nl_to_sql", os.path.join("sql", "nl_to_sql.py")
)
sql_module = importlib.util.module_from_spec(spec_sql)
spec_sql.loader.exec_module(sql_module)

generate_sql = sql_module.generate_sql
run_sql = sql_module.run_sql
explain_result = sql_module.explain_result

# RAG
spec_embed = importlib.util.spec_from_file_location(
    "embedder", os.path.join("rag", "embedder.py")
)
embed_module = importlib.util.module_from_spec(spec_embed)
spec_embed.loader.exec_module(embed_module)

create_embeddings = embed_module.create_embeddings

spec_ret = importlib.util.spec_from_file_location(
    "retriever", os.path.join("rag", "retriever.py")
)
ret_module = importlib.util.module_from_spec(spec_ret)
spec_ret.loader.exec_module(ret_module)

retrieve_reviews = ret_module.retrieve_reviews
