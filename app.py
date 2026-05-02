%%writefile app.py

import streamlit as st
import pandas as pd
import sqlite3
from langchain_community.utilities import SQLDatabase
from langchain.agents import create_sql_agent
from langchain_groq import ChatGroq
import plotly.express as px
import os

os.environ["GROQ_API_KEY"] = "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"

st.title("📊 AI SQL Data Analyst")

uploaded_file = st.file_uploader("train.csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write(df.head())

    conn = sqlite3.connect("data.db")
    df.to_sql("data_table", conn, if_exists="replace", index=False)

    db = SQLDatabase.from_uri("sqlite:///data.db")

    llm = ChatGroq(model="llama-3.3-70b-versatile")

    agent = create_sql_agent(llm=llm, db=db, verbose=True)

    query = st.text_input("Ask your question")

    if query:
        response = agent.run(query)
        st.write("### Answer")
        st.write(response)
