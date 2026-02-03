import requests, re, os
import streamlit as st


def get_webhook_url():
    """Safely resolve the webhook URL from (1) Streamlit secrets, (2) env var, or (3) None.
    Avoids raising at import time so the app can load even when secrets are not provided.
    """
    # prefer streamlit secrets, then environment variable
    url = None
    try:
        url = st.secrets.get("WEBHOOK_URL") if hasattr(st, "secrets") else None
    except Exception:
        # defensive: older/odd Streamlit states
        url = None
    return url or os.environ.get("WEBHOOK_URL")


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
            # validate inputs first
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

            webhook = get_webhook_url()

            # If no webhook is configured, offer a safe "simulate" path for local dev
            if not webhook:
                st.warning("No `WEBHOOK_URL` configured — message will not be sent.")
                simulate = st.checkbox("Simulate send (local test)", value=True, help="Do not perform network request; useful for local testing.")
                if not simulate:
                    st.info("Configure `WEBHOOK_URL` in `.streamlit/secrets.toml` or set the WEBHOOK_URL env var to enable sending.")
                    st.stop()

            # Prepare the data payload
            data = {
                "name": name,
                "last_name": last_name,
                "email": email,
                "message": message,
            }

            if not webhook:
                # developer/testing path — don't actually send
                st.success("Simulation: message prepared (not sent).")
                st.json(data)
                return

            # production path — attempt to send
            try:
                response = requests.post(webhook, json=data, timeout=10)
            except Exception as exc:
                st.error(f"Failed to send message: {exc}")
                st.stop()

            if response.status_code != 200:
                st.error(f"Failed to send your message (status {response.status_code}). Please try again later.", icon="🚨")
            else:
                st.success("Your message has been sent successfully!")
