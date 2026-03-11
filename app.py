import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Talking Rabbit", layout="wide")

st.title("🐰 Talking Rabbit - Conversational Data Analytics")

st.write("Upload a CSV and ask questions about your data.")

# Upload CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    st.subheader("Preview of Data")
    st.dataframe(df)

    question = st.text_input("Ask a question about your data")

    if question:

        question = question.lower()

        # Highest revenue region
        if "highest revenue" in question and "region" in question:

            result = df.groupby("Region")["Revenue"].sum().idxmax()
            st.success(f"Region with highest revenue: {result}")

            chart = df.groupby("Region")["Revenue"].sum()
            st.bar_chart(chart)

        # Total revenue
        elif "total revenue" in question:

            total = df["Revenue"].sum()
            st.success(f"Total Revenue: {total}")

        # Revenue by region
        elif "revenue by region" in question:

            chart = df.groupby("Region")["Revenue"].sum()

            st.write("Revenue by Region")
            st.bar_chart(chart)

        # Monthly trend
        elif "trend" in question or "monthly" in question:

            if "Date" in df.columns:

                trend = df.groupby("Date")["Revenue"].sum()

                st.write("Revenue Trend")
                st.line_chart(trend)

        else:

            st.warning("I couldn't understand the question. Try asking about revenue, region, or trend.")