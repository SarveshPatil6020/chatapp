import streamlit as st
import pandas as pd
from datetime import datetime
import os

# CSV file name
CSV_FILE = 'data.csv'

# Ensure CSV exists with required columns
def init_csv():
    required_columns = ['message', 'date', 'time', 'user']
    
    # Case 1: File doesn't exist
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=required_columns)
        df.to_csv(CSV_FILE, index=False)
    
    # Case 2: File exists but is empty (no headers)
    elif os.path.getsize(CSV_FILE) == 0:
        df = pd.DataFrame(columns=required_columns)
        df.to_csv(CSV_FILE, index=False)

    # Case 3: File exists, maybe missing some columns
    else:
        df = pd.read_csv(CSV_FILE)
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            for col in missing_cols:
                df[col] = ''
            df.to_csv(CSV_FILE, index=False)


# Load chat history
def load_chat():
    df = pd.read_csv(CSV_FILE)
    return df

# Save new message
def save_message(message, user):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    new_row = pd.DataFrame([[message, date, time, user]], columns=['message', 'date', 'time', 'user'])
    new_row.to_csv(CSV_FILE, mode='a', header=False, index=False)

# Main Streamlit App
def main():
    st.set_page_config(page_title="CSV Chat App", layout="centered")
    st.title("📩 Simple CSV Chat App")

    init_csv()

    # Sidebar for user selection
    user = st.sidebar.selectbox("Select your user", ["User A", "User B"])

    st.subheader("💬 Chat History")
    chat_df = load_chat()
    for i, row in chat_df.iterrows():
        with st.chat_message(row["user"]):
            st.markdown(f"**{row['user']}** [{row['time']}]")
            st.markdown(row["message"])

    st.subheader("➕ Send Message")
    with st.form("message_form", clear_on_submit=True):
        message = st.text_input("Type your message:")
        submitted = st.form_submit_button("Send")
        if submitted and message.strip():
            save_message(message.strip(), user)
            st.rerun()

if __name__ == "__main__":
    main()