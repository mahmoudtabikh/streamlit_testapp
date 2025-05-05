import streamlit as st

from forms.contact import contact_form

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
    st.write(
        "Machine Learning Engineer | assisting in training models and making data.driven decision making."
    )
    if st.button(":material/mail: Contact me"):
        show_contact_form()

# --- ABOUT ME SECTION ---
st.write("\n")
st.subheader("Experience & Qualifications", anchor=False)
st.write(
    """
    **Machine Learning Engineer** at [TrinamiX GmbH](https://trinamixsensing.com/) (July 2020 - Present)
    - Delivered high-performing segmentation and classification models using U-Net, YOLO, and EfficientNet, achieving high accuracy in tasks such as facial region detection and laser spot classification across diverse and noisy datasets.
    - Built and led end-to-end ML development workflows, mentoring junior engineers while designing modular Python pipelines for data loading, training, and evaluation — significantly improving team productivity and model iteration speed.
    - Developed clean and maintainable codebases that made it easy for other developers to understand, extend, and deploy models — reducing onboarding time and simplifying collaboration across the team.
    - Increased model reliability and reduced bugs by introducing consistent ways to handle data and evaluate models, helping avoid common training issues and saving hours of debugging time.
    """
)

st.write(
    """
    **Hardware QA Engineer** at [Cognex Coroporation](https://www.cognex.com/) (February 2018 - June 2020)
    - Designed and implemented a user-friendly hardware interface GUI and testing application using Python and Raspberry Pi, enabling efficient device testing and control.
    - Leveraged data visualization techniques to effectively communicate testing and development results for various projects, enhancing decision-making and collaboration among cross-functional teams.
    - Conducted regular firmware updates on devices to ensure optimal performance, security, and compatibility with evolving requirements.
    - Developed automated tests utilizing Python, Linux, and Raspbian Control for rigorous robustness testing, enhancing product reliability and stability.
    - Orchestrated comprehensive test plans, meticulously crafting test procedures, and generating detailed test reports to provide clear insights into product performance.
    - Investigated production issues with a keen eye for detail, diagnosing and resolving challenges promptly.
    - Performed rigorous testing on both Fixed Mount and Handheld devices, along with associated Logistics accessories, ensuring product quality and reliability.
    """
)


st.write(
    """
    **Social Field Assistant** at [Norwegian Refugee Council](https://www.nrc.no/) (September 2016 - September 2017)
    - Organizing and maintaining the global beneficiaries' database.
    """
)

# --- SKILLS SECTION ---
st.write("\n")
st.subheader("Skills", anchor=False)
st.write(
    """
    - **Programming Languages**: Python, R, SQL
    - **Machine Learning**: Scikit-learn, TensorFlow, Keras
    - **Data Visualization**: Matplotlib, Seaborn, Plotly
    - **Big Data Technologies**: Hadoop, Spark
    - **Cloud Technologies**: AWS, Azure
    """
)
# --- EDUCATION SECTION ---
st.write("\n")
st.subheader("Education", anchor=False)
st.write(
    """
    - **Master's program in Machine Learning and AI** at [Arizona State University ](https://www.asu.edu/) (september 2021 - Febuary 2022)
    """
)
st.write(
    """
    - **Electrical Engineering particpant** at [RWTH Aachen](https://www.rwth-aachen.de/go/id/a/?lidx=1) (September 2017 - Feburary 2018)
    """
)
st.write(
    """
    - **Bachelor of Engineering in Electrical Engineering** at [Notre Dame University - Louaize](https://www.ndu.edu.lb/home) (2011 - 2016)
    """
)
# --- HOBBIES SECTION ---
st.write("\n")
st.subheader("Hobbies", anchor=False)
st.write(
    """
    - **Reading**: I enjoy reading books on machine learning, data science, and artificial intelligence.
    - **Traveling**: I love to travel and explore new cultures.
    - **Sports**: I enjoy playing football and basketball.
    """
)
