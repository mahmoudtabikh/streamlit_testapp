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

# --- EXPERIENCE SECTION ---
st.markdown("## Work Experience")

st.markdown(
    """
    ### Data Scientist at [TrinamiX GmbH](https://trinamixsensing.com/)  
    ##### Germany, Ludwigshafen am Rhein | July 2020 - Present
    - Worked on production ML systems for segmentation, classification, and liveness detection, covering dataset definition, train/validation splits, deployment, and iterative improvement with QA.
    - Owned segmentation and binary classification work, including **architecture selection** and incremental improvements to enhance robustness and scalability.
    - Introduced **segmentation-based methods** to handle occlusions, extending system functionality beyond previous capabilities.
    - Improved inference performance by scaling **EfficientNet models** and exploring lighter architectures to meet real-time and certification constraints.
    - Delivered models for demos and certification tests under tight deadlines, ensuring stable and reliable behavior in high-stakes scenarios.
    - Supported the team through **code reviews, mentoring junior data scientists, and technical interviews**.
    - Collaborated closely with system testing, recording, and deployment teams to ensure **model behavior aligns with real-world requirements**.
    - Managed **feature development, user stories, releases, and PRs using Azure DevOps**, planning sprints and maintaining code quality.
    """
)

st.markdown(
    """
    ### Hardware QA Engineer at [Cognex Corporation](https://www.cognex.com/)  
    ##### Germany, Aachen | February 2018 - June 2020
    - Designed and developed internal software tools in Python, including a **GUI-based hardware control and testing application** on Raspberry Pi.
    - Built **automated testing frameworks** using Python and Linux (Raspbian) for repeatable robustness and regression testing, reducing manual effort.
    - Defined and executed **test strategies, plans, procedures, and reporting**, providing structured feedback to development teams.
    - Worked across firmware and software boundaries, performing updates and validating system behavior for stability, compatibility, and performance.
    - Analyzed and resolved production and pre-production issues, contributing to faster **root-cause identification** and improved reliability.
    - Conducted **system-level testing** on fixed-mount and handheld devices, ensuring consistent quality across hardware variants.
    """
)

st.markdown(
    """
    ### Social Field Assistant at the [Norwegian Refugee Council](https://www.nrc.no/)  
    ##### Lebanon, Tal Abbas | September 2016 - September 2017
    - Maintained and analyzed beneficiary data to support **eligibility assessments and fair allocation of assistance**.
    - Coordinated with field teams to **collect, verify, and update information** used in decision-making.
    """
)

# --- SECTION DIVIDER ---
st.write(f"<hr style='border: 2px solid {PRIMARY_COLOR}; margin: 20px 0;' />", unsafe_allow_html=True)

# --- SKILLS SECTION ---
st.markdown("## Skills")
st.write(
    """
    It's hard to mention every single skill or technology I have worked with, but here are some of the most relevant ones:
    - **Programming Languages**: Python, SQL
    - **Machine Learning Frameworks**: Scikit-learn, PyTorch
    - **Data Visualization**: Matplotlib, Seaborn, Plotly
    - **Machine vision libraries**: OpenCV, NumPY, Pillow, SciPy and albumentations
    - **Tools**: Git, Jupyter, docker, streamlit, Azure, AWS.
    - **Databases**: Pandas, and some SQL knwoledge.
    """
)

# --- SECTION DIVIDER ---
st.write(f"<hr style='border: 2px solid {PRIMARY_COLOR}; margin: 20px 0;' />", unsafe_allow_html=True)

# --- EDUCATION SECTION ---
st.markdown("## Education")
st.write(
    """
    - **Master's Program in Machine Learning and AI** at [Arizona State University](https://www.asu.edu/) (September 2021 - May 2022)
    - **Electrical Engineering Participant** at [RWTH Aachen](https://www.rwth-aachen.de/go/id/a/?lidx=1) (September 2017 - February 2018)
    - **Bachelor of Engineering in Electrical Engineering** at [Notre Dame University - Louaize](https://www.ndu.edu.lb/home) (2011 - 2016)
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
    - **Cooking**: I am an avid home cook and enjoy experimenting with new recipes and cuisines.
    - **Football**: I enjoy watching football and playing for my town's club, SG Limburgerhof.
    """
)