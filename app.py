# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime

# Ensure queries.csv exists
CSV_FILE = "queries.csv"
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["Email", "Query", "Timestamp"]).to_csv(CSV_FILE, index=False)

# Set page configuration
st.set_page_config(page_title="Ask Ky’ra – Your Internship Assistant", layout="centered")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Custom styling
st.markdown(
    """
    <style>
    .main {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
    }
    .stTextInput > div > input {
        border: 1px solid #ccc;
        border-radius: 5px;
    }
    .stTextArea > div > textarea {
        border: 1px solid #ccc;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header and welcome message
st.markdown("<h1 style='text-align: center; color: #2e7d32;'>👋 Ask Ky’ra – Your Internship Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Welcome to the Ky’ra Assistant! Enter your query below, and Ky’ra will assist you with your internship questions.</p>", unsafe_allow_html=True)

# Input fields
st.subheader("Your Details")
email_input = st.text_input("Student Email", placeholder="student123@college.edu", help="Enter your college email address.")
query_text = st.text_area("What would you like to ask Ky’ra?", height=150, placeholder="E.g., How can I prepare for my internship interview?")

# Function to call Ky’ra FastAPI backend
def call_kyra_agent_api(email, query):
    try:
        url = "https://kyra.kyras.in/v1/submit-query"
        payload = {"user_email": email, "user_query": query}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("response", "Ky’ra: Thank you for your query. I’ll get back to you soon!")
        else:
            return f"Error: Could not get a response from Ky’ra (Status code: {response.status_code})"
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ky’ra backend: {str(e)}"

# Function to save queries to CSV
def save_query(email, query, timestamp):
    new_row = pd.DataFrame([[email, query, timestamp]], columns=["Email", "Query", "Timestamp"])
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
    df.to_csv(CSV_FILE, index=False)

# Submit button logic
if st.button("Submit", type="primary"):
    if not email_input or not query_text:
        st.error("Please enter both a valid email and a query.")
    else:
        try:
            timestamp = datetime.now().strftime("%d-%m-%Y %H:%M")
            username = email_input.split("@")[0].capitalize()
            response = call_kyra_agent_api(email_input, query_text)
            save_query(email_input, query_text, timestamp)
            st.session_state.chat_history.append({
                "email": email_input,
                "query": query_text,
                "response": response,
                "timestamp": timestamp
            })
            st.success("Your query has been submitted successfully!")
            st.markdown("**🧠 Ky’ra’s Response:**")
            st.info(response)
        except Exception as e:
            st.error(f"Failed to process query: {str(e)}")

# Display chat history
if st.session_state.chat_history:
    st.markdown("**🧾 Chat History:**")
    for i, entry in enumerate(st.session_state.chat_history):
        st.markdown(f"**{i+1}.** *{entry['email']}*: {entry['query']} *(submitted at {entry['timestamp']})*")
        st.markdown(f"   *Ky’ra*: {entry['response']}")
        st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)

# Note about CSV storage
st.markdown("*Note: Queries are saved in 'queries.csv' in the root folder of the Streamlit app environment.*")