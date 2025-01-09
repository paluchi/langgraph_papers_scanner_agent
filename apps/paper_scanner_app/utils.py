import os

from google.oauth2 import service_account
import streamlit as st


BIGQUERY_GOOGLE_APPLICATION_CREDENTIALS = os.getenv(
    "BIGQUERY_GOOGLE_APPLICATION_CREDENTIALS", None
)


if not BIGQUERY_GOOGLE_APPLICATION_CREDENTIALS:
    st.error(
        "Please set the environment variable BIGQUERY_GOOGLE_APPLICATION_CREDENTIALS to store the results in BigQuery."
    )
    st.stop()


# I'm using a different service account file for BigQuery
bigquery_credentials = service_account.Credentials.from_service_account_file(
    BIGQUERY_GOOGLE_APPLICATION_CREDENTIALS
)


BIGQUERY_TABLE_ID = os.getenv("BIGQUERY_TABLE_ID", None)

if not BIGQUERY_TABLE_ID:
    st.error(
        "Please set the environment variable BIGQUERY_TABLE_ID to store the results in BigQuery."
    )
    st.stop()


# IS_DEV = os.getenv("IS_DEV", "False") == "True"
IS_DEV = False
