import io
import streamlit as st
from PIL import Image
import numpy as np
import cv2
from ultralytics import YOLO

# NOTE: `st.set_page_config()` must be called once in the main entrypoint
# (streamlit_app.py). Do not call it from page modules to avoid
# StreamlitSetPageConfigMustBeFirstCommandError.
st.title("Background Remover — remove & download transparent images (PNG) ✂")

# Load model once and reuse
@st.cache_resource
def load_model(path: str = "yolov8n-seg.pt"):
    try:
        model = YOLO(path)
    except Exception as e:
        st.error(f"Failed to load segmentation model: {e}")
        raise
    return model

model = load_model()

st.markdown("Upload an image, select the detected instances you want to keep, refine the mask, then download a PNG with a transparent background.")
st.markdown("I created this page because many websites are charging for this simple functionality — enjoy! 😊")

uploaded = st.file_uploader(
    "Upload image (jpg, png)",
    key="bg_upload_v2",
)

if not uploaded:
    st.info("No image uploaded yet — try a photo with clear foreground (people, objects).")
    st.stop()

# runtime validation + open
uploaded_name = getattr(uploaded, "name", "")
if not uploaded_name.lower().endswith((".jpg", ".jpeg", ".png")):
    st.error("Unsupported file extension. Please upload a JPG/JPEG/PNG image (extensions are case-insensitive).")
    st.stop()

try:
    image = Image.open(uploaded).convert("RGB")
except Exception as e:
    st.error(f"Unable to open image: {e}")
    st.stop()

width, height = image.size
st.image(image, caption="Original image", use_container_width=True)

# Run segmentation
if st.button("Run background removal"):
    with st.spinner("Running segmentation..."):
        results = model.predict(image, task="segment", verbose=False)
        if len(results) == 0:
            st.error("No results from the segmentation model.")
            st.stop()
        res = results[0]

        # Try to get masks as a (N, H, W) boolean numpy array
        masks = None
        try:
            # ultralytics >=8: res.masks.data is a torch or numpy array
            masks = getattr(res.masks, "data", None)
            if masks is None:
                # fallback: res.masks.xy or res.masks.data (older/newer APIs)
                masks = np.asarray(res.masks)  # may fail
        except Exception:
            masks = None

        if masks is None:
            st.error("Could not extract masks from model output.")
            st.stop()

        # Ensure masks is numpy boolean array with shape (N, H, W)
        if hasattr(masks, "cpu"):
            masks = masks.cpu().numpy()
        masks = np.asarray(masks)
        # Some ultralytics builds return floats in [0,1] or bools; threshold if needed
        if masks.dtype != np.bool_:
            masks = masks > 0.5

        num_instances = masks.shape[0]
        names = []
        confidences = []
        for i, box in enumerate(getattr(res, "boxes", [])):
            cls = int(box.cls) if hasattr(box, "cls") else None
            name = res.names[cls] if (cls is not None and cls in res.names) else f"instance_{i}"
            conf = float(box.conf) if hasattr(box, "conf") else 1.0
            names.append(name)
            confidences.append(conf)

        # Build selectable labels
        labels = []
        for i in range(num_instances):
            label = f"{i+1}: {names[i] if i < len(names) else 'object'} ({confidences[i]:.2f})"
            labels.append(label)

        if len(labels) == 0:
            # fallback label indices
            labels = [f"{i+1}: instance" for i in range(num_instances)]

        st.subheader("Detected instances")
        selected = st.multiselect("Select instances to KEEP (their foreground will be preserved)", options=labels, default=[l for l in labels if "person" in l.lower()][:1] or labels)

        if len(selected) == 0:
            st.warning("No instances selected — the output will be fully transparent.")

        # Map selections back to mask indices
        selected_idx = [labels.index(s) for s in selected]

        # Combine masks
        if len(selected_idx) > 0:
            combined = np.any(masks[selected_idx, :, :], axis=0)
        else:
            combined = np.zeros((height, width), dtype=bool)

        # If mask resolution doesn't match the input image, resize/reshape it now.
        # Many segmentation models return masks at a different internal resolution.
        if combined.ndim != 2:
            st.warning(f"Unexpected mask shape {combined.shape}; attempting to coerce to 2D.")
            combined = np.asarray(combined).squeeze()

        mask_h, mask_w = combined.shape
        if (mask_h, mask_w) != (height, width):
            # If mask is a flattened array matching pixels, reshape; otherwise resize.
            if mask_h * mask_w == height * width:
                try:
                    combined = combined.reshape((height, width))
                    st.info("Reshaped mask to image size.")
                except Exception:
                    combined = cv2.resize(combined.astype('uint8'), (width, height), interpolation=cv2.INTER_NEAREST).astype(bool)
                    st.info("Resized mask to image size (fallback reshape failed).")
            else:
                combined = cv2.resize(combined.astype('uint8'), (width, height), interpolation=cv2.INTER_NEAREST).astype(bool)
                st.info(f"Resized mask from {(mask_h, mask_w)} to {(height, width)}")

        # Refinement options
        st.subheader("Refine mask 🔧")
        col1, col2, col3 = st.columns(3)
        with col1:
            dilate = st.slider("Expand (px)", 0, 50, 4)
        with col2:
            erode = st.slider("Contract (px)", 0, 50, 0)
        with col3:
            feather = st.slider("Feather (px)", 0, 80, 8)

        # Apply morphological ops
        kernel_size = max(1, dilate - erode)
        if kernel_size > 0:
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size * 2 + 1, kernel_size * 2 + 1))
            combined = cv2.dilate(combined.astype('uint8'), kernel)
            if erode > 0:
                ek = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (erode * 2 + 1, erode * 2 + 1))
                combined = cv2.erode(combined, ek)
            combined = combined.astype(bool)

        # Feathering via gaussian blur on float mask
        alpha = combined.astype('uint8') * 255
        if feather > 0:
            blur = cv2.GaussianBlur(alpha, (feather // 2 * 2 + 1, feather // 2 * 2 + 1), 0)
            alpha = blur

        # Build RGBA result
        rgb = np.array(image).astype('uint8')

        # Defensive check: alpha must match RGB height/width
        if alpha.ndim != 2 or alpha.shape != rgb.shape[:2]:
            st.warning(f"Mask/alpha shape {alpha.shape} doesn't match image shape {rgb.shape[:2]} — resizing alpha.")
            try:
                alpha = cv2.resize(alpha, (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_LINEAR)
            except Exception as e:
                st.error(f"Failed to resize alpha channel: {e}")
                st.stop()

        alpha_channel = alpha.astype('uint8')
        rgba = np.dstack([rgb, alpha_channel])
        out_pil = Image.fromarray(rgba)
        st.subheader("Preview")
        st.image(out_pil, caption="Foreground with transparent background", use_container_width=True)

        # Background replacement options
        st.subheader("Background options")
        bg_choice = st.selectbox("Replace background with", options=["Transparent (PNG)", "Solid color", "Image background"], index=0)
        final_img = out_pil
        if bg_choice == "Solid color":
            color = st.color_picker("Background color", value="#FFFFFF")
            bg = Image.new("RGBA", out_pil.size, color)
            bg.paste(out_pil, mask=out_pil.split()[3])
            final_img = bg.convert("RGBA")
            st.image(final_img, caption="Preview with solid background", use_container_width=True)
        elif bg_choice == "Image background":
            bg_file = st.file_uploader(
                "Upload background image (optional)",
                key="bg_bgimg_v2",
            )
            if bg_file:
                if not getattr(bg_file, "name", "").lower().endswith((".jpg", ".jpeg", ".png")):
                    st.error("Unsupported background image extension. Use JPG/JPEG/PNG (case-insensitive).")
                else:
                    try:
                        bg_img = Image.open(bg_file).convert("RGBA")
                    except Exception as e:
                        st.error(f"Unable to open background image: {e}")
                    else:
                        bg_img = bg_img.resize(out_pil.size)
                        bg_img.paste(out_pil, mask=out_pil.split()[3])
                        final_img = bg_img
                        st.image(final_img, caption="Preview with image background", use_container_width=True)

        # Download
        buf = io.BytesIO()
        # If transparent selected, save PNG to preserve alpha
        download_format = "PNG" if bg_choice == "Transparent (PNG)" else "PNG"
        final_img.save(buf, format=download_format)
        buf.seek(0)

        st.download_button(label="Download image", data=buf, file_name="background_removed.png", mime="image/png")

        st.success("Background removal complete — download ready ✅")

        st.markdown(
            "> Tips: For best results use photos with clear foreground/background separation. Use the refinement sliders to remove haloing at edges."
        )
else:
    st.info("Click **Run background removal** to start segmentation and mask creation.")
