import requests, re
import streamlit as st


WEBHOOK_URL = st.secrets["WEBHOOK_URL"]

def is_valid_email(email):
    """Check if the email is valid."""
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_pattern, email) is not None

def contact_form():
    with st.form("contact_form", clear_on_submit=False):
        name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        message = st.text_area("Your Message")
        email = st.text_input("Email")
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            if not WEBHOOK_URL:
                st.error("Email service is not configured. Please try again later.")
                st.stop()
            if not name:
                st.error("Please enter your name", icon="🚨")
                st.stop()
            if not last_name:
                st.error("Please enter your last name", icon="🚨")
                st.stop()
            if not email:
                st.error("Please enter your email", icon="🚨")
                st.stop()
            if not message:
                st.error("Please enter your message", icon="🚨")
                st.stop()
            if not is_valid_email(email):
                st.error("Please enter a valid email address", icon="🚨")
                st.stop()

            # Prepare the data payload and send it to the webhook URL
            data = {
                "name": name,
                "last_name": last_name,
                "email": email,
                "message": message,
            }
            response = requests.post(
                WEBHOOK_URL,
                json=data,
            )
            if response.status_code != 200:
                st.error(f"Failed to send your message with code {response.status_code}. Please try again later.", icon="🚨")
                st.stop()
            else:
                st.success("Your message has been sent successfully!")
