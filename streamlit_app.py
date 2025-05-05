import streamlit as st

st.set_page_config(page_title="My Streamlit App", layout="centered")


# --- PAGE SETUP ---

about_page = st.Page(
    title="About me",
    page="pages/about_me.py",
    icon=":material/account_circle:",
    default=True,
)

project_1_page = st.Page(
    title="House Loan Calculator",
    page="pages/house_loan_calculator.py",
    icon=":material/bar_chart:"
)

project_2_page = st.Page(
    title="YOLO v11 Segmentation Model",
    page="pages/segmentation_model.py",
    icon=":material/smart_toy:"
)


project_3_page = st.Page(
    title="Chat GPT Chatbot",
    page="pages/chat_bot.py",
    icon=":material/smart_toy:"
)

# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
pg = st.navigation(
    {
        "Info": [about_page],
        "Projects": [project_1_page, project_2_page, project_3_page],
    }
)

# --- SHARED ON ALL PAGES ---
from PIL import Image
img = Image.open("assets/profile_image.png")
st.logo(img)
st.sidebar.text("Made by Mahmoud Tabikh")

# --- RUN NAVIGATION ---
pg.run()
