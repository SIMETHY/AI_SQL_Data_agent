import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from langchain_groq import ChatGroq

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="AI SQL Analyst", layout="wide")

st.title("📊 AI SQL Data Analyst")

# ---------------------------
# API KEY
# ---------------------------
import os
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# ---------------------------
# MODEL (with fallback)
# ---------------------------
def get_llm():
    models = [
        "llama-3.3-70b-versatile",
        "mixtral-8x7b-32768"
    ]
    for m in models:
        try:
            return ChatGroq(model=m, temperature=0)
        except:
            continue
    st.error("No working model found")
    st.stop()

llm = get_llm()

# ---------------------------
# FILE UPLOAD
# ---------------------------
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    conn = sqlite3.connect("data.db")
    df.to_sql("data_table", conn, if_exists="replace", index=False)

    # ---------------------------
    # USER QUERY
    # ---------------------------
    query = st.text_input("💬 Ask your question")

    if query:
        TABLE_NAME = "data_table"

        columns = df.columns.tolist()
        schema = "Columns:\n" + "\n".join([f"- {col}" for col in columns])

        # SQL Generation
        sql_prompt = f"""
        You are an expert SQL generator.

        Table: {TABLE_NAME}

        {schema}

        Rules:
        - ALWAYS use table name: {TABLE_NAME}
        - Use exact column names
        - Wrap columns with spaces in double quotes
        - Return ONLY SQL
        - No markdown

        Question: {query}
        """

        raw_sql = llm.invoke(sql_prompt).content
        sql_query = raw_sql.replace("```sql", "").replace("```", "").strip()

        st.subheader("🧾 SQL Query")
        st.code(sql_query, language="sql")

        # Execute SQL
        try:
            result_df = pd.read_sql_query(sql_query, conn)

            st.subheader("📊 Result")
            st.dataframe(result_df)

            # Visualization
            if result_df.shape[1] > 1:
                fig = px.bar(
                    result_df,
                    x=result_df.columns[0],
                    y=result_df.columns[1],
                    title="📊 Visualization",
                    template="plotly_dark"
                )
                st.plotly_chart(fig)

            # AI Answer
            answer_prompt = f"""
            Answer clearly based on the result.

            Question: {query}
            Result: {result_df.head(5).to_string(index=False)}
            """

            final_answer = llm.invoke(answer_prompt)

            st.subheader("🤖 AI Answer")
            st.write(final_answer.content)

        except Exception as e:
            st.error(f"SQL Error: {e}")
