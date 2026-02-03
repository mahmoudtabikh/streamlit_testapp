# Streamlit Test App — demo & developer notes 🚀

Live demo / personal page: https://YOUR-WEBSITE.example.com  
> Replace the URL above with your public webpage or demo link — it will appear at the top of the repo and in any README preview.

Short description
- A compact Streamlit multipage demo showcasing image segmentation (background removal), an on-device binary-classification explorer (with Grad‑CAM), and developer tooling for robust local demos.

Key features (what I implemented) ✅
- Background Remover (`pages/background_removal.py`)
  - YOLOv8 segmentation (checked-in `yolov8n-seg.pt`), mask refinement (dilate/erode/feather), precise mask resizing and RGBA export.
  - Download transparent PNGs and replace backgrounds with solid colors or images.
- Binary Classification Explorer (`pages/binary_classification.py`)
  - On-device linear-probe training on pretrained features (ResNet18 / MobileNetV2), quick evaluation UI, and Grad‑CAM explainability with downloadable heatmaps.
- Segmentation demo (`pages/segmentation_model.py`) — smaller, focused example of YOLOv8 masks.
- Developer ergonomics (`streamlit_app.py`)
  - Dev Mode fallbacks, cache & session-state clearing tools, robust upload handling (case-insensitive extensions), and informative error messages.
- Safe-by-default changes
  - Removed/archived the unreliable LLM chatbot from the public UI (archived in repo history), fixed import-time secret reads, and prevented UI crashes caused by emoji/widget state.

Where to find the main code (quick map) 🗺️
- App entry: `streamlit_app.py`
- Background remover: `pages/background_removal.py`
- Segmentation demo: `pages/segmentation_model.py`
- Binary classifier + Grad‑CAM: `pages/binary_classification.py`
- Contact form / secrets handling: `forms/contact.py`
- Developer/dev-tests: `tests/test_deprecations.py`, `.github/workflows/ci.yml`

CI & tests
- A lightweight static CI test prevents reintroducing deprecated APIs: `pytest -q tests/test_deprecations.py`.
- GitHub Actions workflow provided in `.github/workflows/ci.yml` — runs on push/PR.

Developer notes & status
- Production-ready: core features (background remover, binary explorer, segmentation demo) are implemented and wired into navigation.
- Archived: the LLM chatbot was intentionally removed from the UI due to reliability/hallucination concerns; the code is preserved in repo history if its would be restored for research.
- Recommended next steps: (1) set your live-demo URL at the top of this README, (2) add a small example dataset for the Binary Explorer, (3) enable CI badge + optional auto-deploy.

Contact & contributions
- For quick help, open an issue or push a branch and ask me to: verify remote HEAD, run the app and paste the cleaned terminal log, or add an example dataset and demo GIF.

License
- MIT — feel free to reuse or adapt for demos and internal prototypes.

---