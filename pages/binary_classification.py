import io
import time
from typing import Tuple, List

import streamlit as st
from PIL import Image
import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms, models

# Page
st.title("Binary Classification Explorer — end-to-end + explainability 🔍")
st.markdown(
    "Upload a few positive/negative examples, train a tiny linear head on pretrained features (ResNet18 or MobileNetV2), "
    "then test on an image/patch. View confidence and a Grad-CAM heatmap for explainability."
)

# -- Utilities -----------------------------------------------------------------

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

@st.cache_resource
def load_backbone(name: str = "resnet18"):
    name = name.lower()
    if name == "resnet18":
        # prefer the new `weights=` enum when available (torchvision >= 0.13+)
        try:
            from torchvision.models import ResNet18_Weights
            m = models.resnet18(weights=ResNet18_Weights.DEFAULT)
        except Exception:
            # fallback for older torchvision versions
            m = models.resnet18(pretrained=True)
        feat_dim = m.fc.in_features
        # remove final fc
        backbone = nn.Sequential(*list(m.children())[:-2])
        target_layer = m.layer4
    elif name == "mobilenet_v2":
        try:
            from torchvision.models import MobileNet_V2_Weights
            m = models.mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT)
        except Exception:
            m = models.mobilenet_v2(pretrained=True)
        feat_dim = m.classifier[1].in_features
        backbone = nn.Sequential(*list(m.features))
        target_layer = m.features[-1]
    else:
        raise ValueError("Unsupported backbone")

    backbone.eval()
    backbone.to(DEVICE)
    return backbone, feat_dim, target_layer


def preprocess_pil(img: Image.Image, size: Tuple[int, int] = (224, 224)) -> torch.Tensor:
    tf = transforms.Compose([
        transforms.Resize(size),
        transforms.CenterCrop(size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    return tf(img).unsqueeze(0)


def extract_features(batch: torch.Tensor, backbone: nn.Module) -> torch.Tensor:
    """Return global-pooled features (B, C) from backbone."""
    with torch.no_grad():
        x = batch.to(DEVICE)
        feats = backbone(x)  # shape (B, C, H, W)
        gap = F.adaptive_avg_pool2d(feats, 1).reshape(x.shape[0], -1)
    return gap.cpu()


class LinearHead(nn.Module):
    def __init__(self, in_dim: int):
        super().__init__()
        self.linear = nn.Linear(in_dim, 1)

    def forward(self, x):
        return self.linear(x).squeeze(-1)


def train_head(head: nn.Module, features: torch.Tensor, labels: torch.Tensor, epochs: int = 20, lr: float = 1e-2):
    head.to(DEVICE)
    head.train()
    opt = torch.optim.Adam(head.parameters(), lr=lr)
    features = features.to(DEVICE)
    labels = labels.to(DEVICE).float()
    losses = []
    for ep in range(epochs):
        opt.zero_grad()
        logits = head(features)
        loss = F.binary_cross_entropy_with_logits(logits, labels)
        loss.backward()
        opt.step()
        losses.append(loss.item())
    head.eval()
    return head, losses


def predict_image(img: Image.Image, backbone: nn.Module, head: nn.Module, size=(224, 224)):
    t = preprocess_pil(img, size=size)
    feats = extract_features(t, backbone)
    with torch.no_grad():
        logits = head(torch.from_numpy(feats.numpy()))
        prob = torch.sigmoid(logits).item()
    return prob


# --- Grad-CAM (simple) ------------------------------------------------------

def find_target_conv(module: nn.Module):
    # find last Conv2d in module
    last = None
    for m in module.modules():
        if isinstance(m, nn.Conv2d):
            last = m
    return last


def gradcam(img: Image.Image, backbone: nn.Module, head: nn.Module, target_index: int = 1, size=(224, 224)) -> np.ndarray:
    # Prepare
    backbone.to(DEVICE).eval()
    head.to(DEVICE).eval()
    x = preprocess_pil(img, size=size).to(DEVICE)

    # Find conv layer to hook
    target_conv = find_target_conv(backbone)
    if target_conv is None:
        raise RuntimeError("Couldn't find conv layer for Grad-CAM")

    activations = None
    gradients = None

    def forward_hook(module, inp, out):
        nonlocal activations
        activations = out.detach()

    def backward_hook(module, grad_in, grad_out):
        nonlocal gradients
        gradients = grad_out[0].detach()

    fh = target_conv.register_forward_hook(forward_hook)
    # prefer the newer, full backward hook API when available to avoid deprecation warnings
    if hasattr(target_conv, "register_full_backward_hook"):
        bh = target_conv.register_full_backward_hook(backward_hook)
    else:
        bh = target_conv.register_backward_hook(backward_hook)

    # Forward
    backbone.zero_grad()
    head.zero_grad()
    feats = backbone(x)  # (1, C, H, W)
    gap = F.adaptive_avg_pool2d(feats, 1).reshape(1, -1)
    logits = head(gap)
    prob = torch.sigmoid(logits)

    # Backward on the positive logit
    loss = logits[0]
    loss.backward()

    fh.remove()
    bh.remove()

    # Compute weights
    pooled_grads = gradients.mean(dim=[0, 2, 3])  # (C,)
    cam = (activations[0] * pooled_grads[:, None, None]).sum(0)
    cam = F.relu(cam)
    cam = cam.cpu().numpy()
    cam = cv2.resize(cam, img.size)
    cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
    return cam


# --- UI ---------------------------------------------------------------------

col1, col2 = st.columns([1, 2])
with col1:
    backbone_name = st.selectbox("Backbone", ["resnet18", "mobilenet_v2"], index=0)
    backbone, feat_dim, target_layer = load_backbone(backbone_name)

    uploaded_pos = st.file_uploader("Upload positive examples (multiple)", accept_multiple_files=True, key="pos_examples_v2")
    uploaded_neg = st.file_uploader("Upload negative examples (multiple)", accept_multiple_files=True, key="neg_examples_v2")

    use_demo = st.checkbox("Use demo heuristic classifier if not enough examples", value=True)

    # runtime validation will filter unsupported files (handles uppercase extensions from older widget state)

    epochs = st.slider("Train epochs", 1, 200, 30)
    lr = st.number_input("Learning rate", value=1e-2, format="%.5f")

    threshold = st.slider("Decision threshold", 0.0, 1.0, 0.5)

with col2:
    st.write("""
    **Instructions**
    - Provide at least 3 positive and 3 negative images for a simple linear probe.
    - Click **Train classifier** to fit a tiny head on pretrained features.
    - Upload a **Test image** below and optionally crop a patch to evaluate.
    """)

# Prepare dataset
pos_imgs: List[Image.Image] = []
neg_imgs: List[Image.Image] = []

pos_skipped = 0
neg_skipped = 0
for f in uploaded_pos or []:
    name = getattr(f, "name", "")
    if not name.lower().endswith((".jpg", ".jpeg", ".png")):
        pos_skipped += 1
        continue
    try:
        pos_imgs.append(Image.open(f).convert("RGB"))
    except Exception:
        pos_skipped += 1
for f in uploaded_neg or []:
    name = getattr(f, "name", "")
    if not name.lower().endswith((".jpg", ".jpeg", ".png")):
        neg_skipped += 1
        continue
    try:
        neg_imgs.append(Image.open(f).convert("RGB"))
    except Exception:
        neg_skipped += 1

if pos_skipped or neg_skipped:
    st.warning(f"Some uploaded example files were skipped because they could not be opened or had unsupported extensions (skipped pos={pos_skipped}, neg={neg_skipped}).")

trained_head = None
training_losses = None

if st.button("Train classifier"):
    if len(pos_imgs) + len(neg_imgs) < 4:
        if use_demo:
            st.warning("Not enough examples — falling back to a demo heuristic classifier.")
        else:
            st.error("Please provide at least a few positive and negative examples to train the head.")
            st.stop()

    if len(pos_imgs) >= 1 and len(neg_imgs) >= 1:
        # Build features and labels
        imgs = pos_imgs + neg_imgs
        labels = torch.tensor([1] * len(pos_imgs) + [0] * len(neg_imgs))
        batch = torch.cat([preprocess_pil(i) for i in imgs], dim=0)
        feats = extract_features(batch, backbone)  # CPU tensor

        # Train-test split (80/20)
        n = feats.shape[0]
        idx = list(range(n))
        split = int(n * 0.8)
        train_idx = idx[:split]
        val_idx = idx[split:]
        train_feats = feats[train_idx]
        train_labels = labels[train_idx]
        val_feats = feats[val_idx]
        val_labels = labels[val_idx]

        head = LinearHead(feat_dim)
        head, losses = train_head(head, train_feats, train_labels, epochs=epochs, lr=lr)
        trained_head = head
        training_losses = losses

        # Eval
        with torch.no_grad():
            val_logits = head(val_feats)
            val_probs = torch.sigmoid(val_logits)
            val_pred = (val_probs >= threshold).long()
            acc = (val_pred.cpu() == val_labels).float().mean().item() if len(val_labels) > 0 else float('nan')
        st.success(f"Trained head — validation accuracy: {acc:.2f} (n_val={len(val_labels)})")
        st.line_chart(losses)
    else:
        st.info("Falling back to a demo heuristic classifier based on brightness (not ML).")

# Test UI
st.markdown("---")
st.subheader("Test image / patch")
# avoid `type=` to prevent Streamlit deserialization errors with uppercase extensions
test_file = st.file_uploader("Upload test image", key="bc_test_v2")
if test_file is None:
    st.info("Upload a test image to run the classifier and visualize Grad-CAM.")
    st.stop()

# runtime validation for filename extension (case-insensitive)
test_name = getattr(test_file, "name", "")
if not test_name.lower().endswith((".jpg", ".jpeg", ".png")):
    st.error("Unsupported file extension for test image. Please upload JPG/JPEG/PNG (case-insensitive).")
    st.stop()

try:
    test_img = Image.open(test_file).convert("RGB")
except Exception as e:
    st.error(f"Unable to open test image: {e}")
    st.stop()

w, h = test_img.size
st.image(test_img, caption="Test image", use_container_width=True)

col_a, col_b = st.columns(2)
with col_a:
    left = st.slider("Left (px)", 0, max(0, w - 2), 0)
    top = st.slider("Top (px)", 0, max(0, h - 2), 0)
with col_b:
    box_w = st.slider("Width (px)", 10, w - left, min(224, w - left))
    box_h = st.slider("Height (px)", 10, h - top, min(224, h - top))

crop = test_img.crop((left, top, left + box_w, top + box_h))
st.image(crop, caption="Cropped patch", width=224)

# Inference
if trained_head is None and (len(pos_imgs) < 1 or len(neg_imgs) < 1):
    # demo heuristic: mean brightness
    arr = np.array(crop.convert("L")) / 255.0
    score = float(arr.mean())
    prob = score  # brighter -> positive in demo
    st.info("Using demo heuristic classifier (brightness-based). Provide example images and train to use an ML model.")
else:
    if trained_head is not None:
        prob = predict_image(crop, backbone, trained_head, size=(224, 224))
    else:
        # Edge: user supplied examples but didn't train — extract features and fit a 1-step logistic on the fly
        st.info("Fitting a quick linear probe on the supplied examples (one-shot).")
        imgs = pos_imgs + neg_imgs
        labels = torch.tensor([1] * len(pos_imgs) + [0] * len(neg_imgs))
        batch = torch.cat([preprocess_pil(i) for i in imgs], dim=0)
        feats = extract_features(batch, backbone)
        head = LinearHead(feat_dim)
        head, _ = train_head(head, feats, labels, epochs=30, lr=1e-2)
        prob = predict_image(crop, backbone, head, size=(224, 224))

decision = "POSITIVE" if prob >= threshold else "NEGATIVE"
st.metric("Prediction", f"{decision}", f"confidence {prob:.3f}")
st.progress(min(max(prob, 0.0), 1.0))

# Grad-CAM
with st.spinner("Computing Grad-CAM..."):
    try:
        cam = gradcam(crop, backbone, trained_head if trained_head is not None else head, size=(224, 224))
    except Exception as e:
        st.error(f"Grad-CAM failed: {e}")
        cam = None

if cam is not None:
    heat = (cam * 255).astype('uint8')
    heat_color = cv2.applyColorMap(heat, cv2.COLORMAP_JET)
    heat_color = cv2.cvtColor(heat_color, cv2.COLOR_BGR2RGB)
    overlay = (0.5 * np.array(crop.resize((heat_color.shape[1], heat_color.shape[0]))) + 0.5 * heat_color).astype('uint8')
    st.subheader("Grad-CAM heatmap")
    st.image(heat_color, caption="Raw heatmap", width=224)
    st.image(overlay, caption="Overlay", width=224)

    # Download buttons
    buf1 = io.BytesIO()
    Image.fromarray(overlay).save(buf1, format="PNG")
    buf1.seek(0)
    st.download_button("Download overlay PNG", data=buf1, file_name="gradcam_overlay.png", mime="image/png")

    buf2 = io.BytesIO()
    Image.fromarray(heat_color).save(buf2, format="PNG")
    buf2.seek(0)
    st.download_button("Download heatmap PNG", data=buf2, file_name="gradcam_heatmap.png", mime="image/png")

st.markdown("---")
st.caption("This explorer demonstrates a lightweight, explainable binary classifier you can train on-device.")
