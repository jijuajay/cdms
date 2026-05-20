import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ---------------- LOGIN SYSTEM ----------------

USERNAME = "admin"
PASSWORD = "1234"

st.title("Clinical Data Cleaning & Query Management")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if username == USERNAME and password == PASSWORD:

    st.success("Login Successful")

    # --- Upload Master CSV ---
    uploaded_file = st.file_uploader(
        "Upload MasterClinicalData.csv",
        type="csv"
    )

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        st.subheader("Uploaded Data")
        st.dataframe(df)

        # --- Error Detection ---
        st.subheader("Automatic Error Checks")

        # Example 1: DOB in future
        today = pd.to_datetime(datetime.now().date())

        dob_errors = df[
            pd.to_datetime(df["DOB"], errors="coerce") > today
        ]

        if not dob_errors.empty:
            st.warning("DOB errors detected (future dates):")
            st.dataframe(dob_errors)

        # Example 2: Missing values
        missing = df[df.isnull().any(axis=1)]

        if not missing.empty:
            st.warning("Rows with missing values:")
            st.dataframe(missing)

        # Example 3: Heart Rate out of range
        hr_errors = df[
            (df["HeartRate"] < 40) |
            (df["HeartRate"] > 180)
        ]

        if not hr_errors.empty:
            st.warning("Heart rate out of range:")
            st.dataframe(hr_errors)

        # ---------------- QUERY MANAGEMENT ----------------

        QUERY_FILE = "Queries.csv"

        if not os.path.exists(QUERY_FILE):
            pd.DataFrame(
                columns=[
                    "Subject",
                    "Field",
                    "Issue",
                    "Status",
                    "DateRaised",
                    "DateResolved"
                ]
            ).to_csv(QUERY_FILE, index=False)

        def load_queries():
            return pd.read_csv(QUERY_FILE)

        def save_queries(dfq):
            dfq.to_csv(QUERY_FILE, index=False)

        # -------- Raise Query --------

        st.subheader("Raise a Query")

        subject = st.text_input("Subject ID")
        field = st.text_input(
            "Field with issue (e.g., DOB, HeartRate)"
        )
        issue = st.text_area("Describe the issue")

        if st.button("Raise Query"):

            queries = load_queries()

            new_query = {
                "Subject": subject,
                "Field": field,
                "Issue": issue,
                "Status": "Open",
                "DateRaised": datetime.now().strftime("%Y-%m-%d"),
                "DateResolved": ""
            }

            queries = pd.concat(
                [queries, pd.DataFrame([new_query])],
                ignore_index=True
            )

            save_queries(queries)

            st.success("Query raised successfully!")

        # -------- Resolve Query --------

        st.subheader("Resolve a Query")

        queries = load_queries()

        st.dataframe(queries)

        query_index = st.number_input(
            "Enter query row number to resolve",
            min_value=0,
            step=1
        )

        if st.button("Mark as Resolved"):

            if query_index < len(queries):

                queries.loc[query_index, "Status"] = "Resolved"

                queries.loc[
                    query_index,
                    "DateResolved"
                ] = datetime.now().strftime("%Y-%m-%d")

                save_queries(queries)

                st.success("Query resolved successfully!")

            else:
                st.error("Invalid query index")

        # ---------------- REPORTS ----------------

        st.subheader("Query Summary Report")

        open_count = (queries["Status"] == "Open").sum()

        resolved_count = (
            queries["Status"] == "Resolved"
        ).sum()

        st.write(f"Open Queries: {open_count}")
        st.write(f"Resolved Queries: {resolved_count}")

elif username != "" or password != "":
    st.error("Invalid Username or Password")
