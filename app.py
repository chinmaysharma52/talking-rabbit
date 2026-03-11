import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.markdown("""
<style>

.main {
    background-color: #f4f6fb;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1 {
    color: #1f2937;
    text-align: center;
}

h3 {
    text-align: center;
    color: #4b5563;
}

.stFileUploader {
    border: 2px dashed #6366f1;
    padding: 20px;
    border-radius: 12px;
    background-color: white;
}

.stButton>button {
    background-color: #6366f1;
    color: white;
    border-radius: 8px;
    height: 45px;
    width: 100%;
    font-size: 16px;
}

.stButton>button:hover {
    background-color: #4f46e5;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
# 🐰 Talking Rabbit

### Conversational Data Analytics

Upload a CSV file and **ask questions about your data instantly**.
""")
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
