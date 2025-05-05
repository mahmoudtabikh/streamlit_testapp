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

# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
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
