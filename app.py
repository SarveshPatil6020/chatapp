import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
import os
from cryptography.fernet import Fernet
from streamlit_autorefresh import st_autorefresh
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ===============================
# Files
# ===============================
CSV_FILE = "data.csv"
KEY_FILE = "secret.key"

# ===============================
# Generate or Load Encryption Key
# ===============================
def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    else:
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
    return key

KEY = load_key()
cipher = Fernet(KEY)

# ===============================
# Initialize CSV
# ===============================
def init_csv():
    required_columns = ["message", "date", "time", "user", "password", "email"]

    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        df = pd.DataFrame(columns=required_columns)
        df.to_csv(CSV_FILE, index=False)
    else:
        df = pd.read_csv(CSV_FILE)
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""
        df.to_csv(CSV_FILE, index=False)

# ===============================
# Password Hashing
# ===============================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ===============================
# Encrypt / Decrypt
# ===============================
def encrypt_message(msg):
    return cipher.encrypt(msg.encode()).decode()

def decrypt_message(enc_msg):
    try:
        return cipher.decrypt(enc_msg.encode()).decode()
    except:
        return "⚠️ Unable to decrypt message"

# ===============================
# Load Chat
# ===============================
def load_chat():
    return pd.read_csv(CSV_FILE)

# ===============================
# Save Message (encrypted)
# ===============================
def save_message(message, user):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    encrypted_msg = encrypt_message(message)

    new_row = pd.DataFrame(
        [[encrypted_msg, date, time, user, "", ""]],
        columns=["message", "date", "time", "user", "password", "email"]
    )
    new_row.to_csv(CSV_FILE, mode="a", header=False, index=False)

# ===============================
# Create User (stores email also)
# ===============================
def create_user(username, password, email):
    hashed_pass = hash_password(password)
    new_row = pd.DataFrame(
        [["", "", "", username, hashed_pass, email]],
        columns=["message", "date", "time", "user", "password", "email"]
    )
    new_row.to_csv(CSV_FILE, mode="a", header=False, index=False)

# ===============================
# Verify User
# ===============================
def verify_user(username, password):
    df = load_chat()
    user_rows = df[df["user"] == username]

    if user_rows.empty:
        return False

    stored_hash = user_rows["password"].dropna().iloc[0]
    return stored_hash == hash_password(password)

# ===============================
# Send Email
# ===============================
def send_email(to_address):

    from_address = 'sarvesh194025@gmail.com'
    # password = 'djac aodd osrd uysk'  # your Gmail app password
    password = 'lyys szzh wskw qrtz'  # your Gmail app password
    
    try:
        msg = MIMEMultipart()
        msg['From'] = from_address
        msg['To'] = to_address
        msg['Subject'] = "HDFC BANK : Up to Rs. 2,000 Off on Domestic Flights with HDFC Bank Credit Card + Interest Free EMI"

        body = """How to avail the offer?
                    Search and choose your preferred flight.
                    Apply the code at the time of making your booking.
                    Proceed to the payment page and make your payment.
                    Proceed to the payments page and pay via HDFC Debit/Credit Card EMI.
                    
        Regards,
        Chat System
        """

        msg.attach(MIMEText(body, 'plain'))

        # Setup SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_address, password)
        server.sendmail(from_address, to_address, msg.as_string())
        server.quit()

        st.success(f"Email sent to {to_address}")

    except Exception as e:
        st.error(f"Failed to send email: {e}")

# ===============================
# Main App
# ===============================
def main():
    st.set_page_config(page_title="Secure Chat App", layout="centered")
    st_autorefresh(interval=3000, key="chat_refresh")

    init_csv()
    df = load_chat()

    existing_users = sorted(df["user"].dropna().unique().tolist())

    # ===============================
    # Corner Button (Top Right)
    # ===============================
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("🔔"):
            if "user" in st.session_state:
                send_email("taraaa.oberoi.137@gmail.com")
            else:
                st.warning("No email found for this user.")

    st.title("🔐 Secure Chat App")

    # ===============================
    # Login / Signup Sidebar
    # ===============================
    st.sidebar.subheader("👤 Login")

    mode = st.sidebar.radio("Choose option", ["Login", "Create New User"])

    if mode == "Create New User":
        new_user = st.sidebar.text_input("Enter username")
        new_pass = st.sidebar.text_input("Create password", type="password")
        new_email = st.sidebar.text_input("Enter Email Address")

        if st.sidebar.button("Create Account"):
            if new_user and new_pass and new_email:
                create_user(new_user, new_pass, new_email)
                st.sidebar.success("User created! Please login.")
            else:
                st.sidebar.error("Please fill all fields.")

    else:
        if existing_users:
            username = st.sidebar.selectbox("Select user", existing_users)
            password = st.sidebar.text_input("Enter password", type="password")

            if st.sidebar.button("Login"):
                if verify_user(username, password):
                    st.session_state["user"] = username
                else:
                    st.sidebar.error("Invalid password")
        else:
            st.sidebar.info("No users found. Create a new one.")

    if "user" not in st.session_state:
        st.warning("Please login to continue.")
        st.stop()

    user = st.session_state["user"]

    # ===============================
    # Chat Section
    # ===============================
    st.subheader("💬 Chat History")

    today = datetime.now().strftime("%Y-%m-%d")
    chat_df = df[df["date"] == today]

    if chat_df.empty:
        st.info("No messages yet today.")
    else:
        for _, row in chat_df.iterrows():
            if row["message"]:
                with st.chat_message(row["user"]):
                    decrypted_text = decrypt_message(row["message"])
                    st.markdown(f"**{row['user']} [{row['time']}]**: {decrypted_text}")

    # ===============================
    # Send Message
    # ===============================
    st.subheader("➕ Send Message")

    with st.form("send_form", clear_on_submit=True):
        msg = st.text_input("Type your message:")
        send = st.form_submit_button("Send")

        if send and msg.strip():
            save_message(msg.strip(), user)
            st.rerun()


if __name__ == "__main__":
    main()
