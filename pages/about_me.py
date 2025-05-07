import streamlit as st
from forms.contact import contact_form
import streamlit.components.v1 as components

# --- COLOR PALETTE ---
PRIMARY_COLOR = "#2b6cb0"
SECONDARY_COLOR = "#2c5282"
BACKGROUND_COLOR = "#f7fafc"
TEXT_COLOR = "#2d3748"
HIGHLIGHT_COLOR = "#63b3ed"

st.markdown(f"<style>body {{background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};}}</style>", unsafe_allow_html=True)

# --- ABOUT ME PAGE ---
@st.dialog("Contact Me")
def show_contact_form():
    contact_form()

# --- HERO SECTION ---
col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
with col1:
    st.image("assets/profile_image.png", width=230)
with col2:
    st.title("Mahmoud Tabikh", anchor=False)
    st.write(f"<span style='font-size: 1.5em; color: {PRIMARY_COLOR};'><strong>Machine Learning Engineer at TrinamiX GmbH</strong></span>", unsafe_allow_html=True)
    st.write(
        f"<span style='font-size: 1.2em;'>Data scientist | Data Enthusiast</span>",
        unsafe_allow_html=True
    )
    st.write(
        "Assisting in training models and making data-driven decisions, with a focus on computer vision and deep learning."
    )
    if st.button(":material/mail: Contact me"):
        show_contact_form()

# --- SECTION DIVIDER ---
st.write(f"<hr style='border: 2px solid {PRIMARY_COLOR}; margin: 20px 0;' />", unsafe_allow_html=True)

# --- EXPERIENCE SECTION ---
st.markdown(""" ## Experience & Qualifications""")

st.markdown(
    """
    ### 🧠 Machine Learning Engineer at [TrinamiX GmbH](https://trinamixsensing.com/)\n ##### July 2020 - Present
    - Delivered high-performing segmentation and classification models using U-Net, YOLO, and EfficientNet.
    - Reduced model training time by 40% through optimized data pipelines.
    - Developed modular Python pipelines for efficient data loading, training, and evaluation, enhancing team productivity.
    - Led cross-functional collaboration, improving model iteration speed and quality.
    - Established best practices for code quality, reducing bugs and improving model reliability.
    """
)

st.markdown(
    """
    ### 🛠️ Hardware QA Engineer at [Cognex Corporation](https://www.cognex.com/)\n ##### February 2018 - June 2020
    - Designed intuitive hardware interfaces and testing applications using Python and Raspberry Pi.
    - Conducted robust automated testing, improving product stability and reducing downtime.
    - Created detailed test plans and reports, providing clear insights into product quality.
    - Diagnosed and resolved production issues, minimizing operational disruptions.
    """
)

st.markdown(
    """
    ### 🌐 Social Field Assistant at the [Norwegian Refugee Council](https://www.nrc.no/)\n ##### September 2016 - September 2017
    - Managed and organized the global beneficiaries' database, ensuring data accuracy and integrity.
    """
)

# --- SECTION DIVIDER ---
st.write(f"<hr style='border: 2px solid {PRIMARY_COLOR}; margin: 20px 0;' />", unsafe_allow_html=True)

# --- SKILLS SECTION ---
st.markdown("## Skills")
st.write(
    """
    - 🐍 **Programming Languages**: Python, R, SQL
    - 🤖 **Machine Learning Frameworks**: Scikit-learn, TensorFlow, Keras, PyTorch
    - 📊 **Data Visualization**: Matplotlib, Seaborn, Plotly
    - 💾 **Big Data Technologies**: Hadoop, Spark
    - ☁️ **Cloud Technologies**: AWS, Azure
    """
)

# --- SECTION DIVIDER ---
st.write(f"<hr style='border: 2px solid {PRIMARY_COLOR}; margin: 20px 0;' />", unsafe_allow_html=True)

# --- EDUCATION SECTION ---
st.markdown("## Education")
st.write(
    """
    - 🎓 **Master's Program in Machine Learning and AI** at [Arizona State University](https://www.asu.edu/) (September 2021 - May 2022)
    - ⚙️ **Electrical Engineering Participant** at [RWTH Aachen](https://www.rwth-aachen.de/go/id/a/?lidx=1) (September 2017 - February 2018)
    - 📐 **Bachelor of Engineering in Electrical Engineering** at [Notre Dame University - Louaize](https://www.ndu.edu.lb/home) (2011 - 2016)
    """
)

# --- SECTION DIVIDER ---
st.write(f"<hr style='border: 2px solid {PRIMARY_COLOR}; margin: 20px 0;' />", unsafe_allow_html=True)

# --- CERTIFICATIONS SECTION ---
st.markdown("## Certifications")
st.write(
    """
    - **Generative AI with Large Language Models** from [deeplearning.ai](https://www.coursera.org/account/accomplishments/verify/U3B7AXE5RW35) (January 2024)
    - **AI / ML Professional Certification** from [Arizona State University](https://badgr.com/public/assertions/Pym9DnfETD2IcAMCbfAJJw) (May 2022)
    """
)

# --- SECTION DIVIDER ---
st.write(f"<hr style='border: 2px solid {PRIMARY_COLOR}; margin: 20px 0;' />", unsafe_allow_html=True)

# --- HOBBIES SECTION ---
st.markdown("## Hobbies")
st.write(
    """
    - 🍳 **Cooking**: I am an avid home cook and enjoy experimenting with new recipes and cuisines.
    - ⚽ **Football**: I enjoy watching football and playing for my town's club, SG Limburgerhof.
    """
)