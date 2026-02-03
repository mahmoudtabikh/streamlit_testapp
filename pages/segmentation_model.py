import streamlit as st
import cv2
import torch
import numpy as np
from PIL import Image
from ultralytics import YOLO

torch.classes.__path__ = [] # add this line to manually set it to empty. 


st.title("YOLOv8 Segmentation with Streamlit")

# Load model only once
@st.cache_resource
def load_model(model_path="yolov8n-seg.pt"):
    model = YOLO(model_path)
    return model

model = load_model()

# Upload image — avoid using the `type=` widget validation so filenames like `.JPG` don't get rejected by an older serialized widget state
# (we validate the extension at runtime in a case-insensitive way).
uploaded_file = st.file_uploader(
    "Upload an image (jpg, jpeg, png)",
    key="seg_upload_v2",
)

if uploaded_file:
    # runtime validation (case-insensitive) and friendly error messages
    name = getattr(uploaded_file, "name", "")
    if not name.lower().endswith((".jpg", ".jpeg", ".png")):
        st.error("Unsupported file extension. Please upload a JPG/JPEG/PNG image (extensions are case-insensitive).")
        st.stop()

    try:
        image = Image.open(uploaded_file).convert("RGB")
    except Exception as e:
        st.error(f"Unable to open image: {e}")
        st.stop()

    st.image(image, caption="Uploaded Image", use_container_width=True)

    # Run inference
    if st.button("Run YOLO Segmentation"):
        with st.spinner("Segmenting..."):
            results = model.predict(image, task="segment")
            result = results[0]

            # Show masks and boxes on the image
            annotated_frame = result.plot()  # RGB numpy array

            st.image(annotated_frame, caption="YOLO Segmentation Output", use_container_width=True)

            # Optional: show class names and confidence
            st.subheader("Detected Instances")
            for i, box in enumerate(result.boxes):
                cls = result.names[int(box.cls)]
                conf = box.conf.item()
                st.write(f"{i+1}. **{cls}** with confidence {conf:.2f}")
