# Portfolio — Streamlit Test App

Live demo / portfolio page: https://mahmoud-tabikh-aboutme.streamlit.app/

Elevator
- A focused demo of applied ML engineering: robust image segmentation (background removal), an explainable on-device binary-classifier (Grad‑CAM), and pragmatic developer tooling for reliable demos.  
- Emphasis: production-minded fixes (robust upload handling, secrets safety, session-state recovery) and clear trade-offs made for demo reliability.

Highlights
- Built a production-style background-removal pipeline (YOLOv8 + mask refinement → downloadable transparent PNG). Key fixes: deterministic mask resizing, morphological refinement, and alpha composition.
- Implemented an on-device Binary Classification Explorer that trains a linear probe on pretrained features and provides Grad‑CAM explainability — useful for rapid prototyping and client demos.
- Hardened app stability: removed import-time secret access, fixed Streamlit widget deserialization issues (.JPG/.PNG edge cases), added Dev Mode CPU fallbacks and cache/session recovery tools.
- Added lightweight, import-free CI checks to prevent reintroducing deprecated APIs and UI anti-patterns (practical safety guardrails for small ML demos).

Tech summary (short)
- Frameworks: Streamlit (UI), PyTorch (models / torchvision), ultralytics (YOLOv8), OpenCV/Pillow (image I/O), numpy/pandas for utilities.
- Patterns: device-aware fallbacks (GPU→CPU), cached model loading, explainability (Grad‑CAM), runtime-safe secrets access, and small static CI tests.

Review guide — files & things to highlight 🔎
- Core features
  - `pages/background_removal.py` — mask extraction, resizing, morphological refine, RGBA compose & PNG download. (Look at mask-resize + alpha-compose for the bug fix.)
  - `pages/binary_classification.py` — feature extraction, linear-head training loop, and the Grad‑CAM implementation.
  - `pages/segmentation_model.py` — compact YOLOv8 segmentation example and visualization code.
- App scaffolding & robustness
  - `streamlit_app.py` — navigation, developer tools (cache/session clearing), and UI sanitizers.
  - `forms/contact.py` — runtime-safe secrets lookup and webhook simulation for local demos.
- Quality & CI
  - `tests/test_deprecations.py` — static checks preventing risky patterns (no heavy ML imports so CI stays fast).
  - `.github/workflows/ci.yml` — pipeline that runs the static checks on push/PR.

Why these choices matter
- Demonstrates pragmatic engineering: reproducible demos that fail gracefully.
- Balances UX vs. fidelity: checked-in small weights for instant demos, Dev Mode & CPU fallbacks for reproducibility across varied reviewer machines.
- Safety-first: removed brittle features (no public LLM) and added tests to prevent regressions that would break demos.

What to demo — 2 minutes
1. Open the live demo (or run locally) and show the Background Remover: upload a photo → refine mask → download a transparent PNG.  
2. Open Binary Classification Explorer: add a couple of positive/negative images, train the linear head (seconds), show Grad‑CAM heatmap and downloadable artifact.  
3. Sidebar → Developer tools → Clear caches & restart (shows reliability-focused UX).

Talking points / interview prompts (use these to probe depth) 🎯
- Walk me through the mask-resize bug: how did you reproduce it and what fixes did you apply? (Expect: deterministic resizing + unit-checks.)
- Why keep small weights in-repo for demos? Discuss trade-offs and deployment alternatives. (Expect: UX vs. security/cost trade-off.)
- Show the Grad‑CAM implementation and explain limitations for small linear probes.

Quick reproduction (only if needed)
- Minimal: `streamlit run streamlit_app.py` (app contains in-app Developer tools for common recovery actions).  
- Full dev: see `requirements.txt` if you need to run locally, but reproduction steps are intentionally de-emphasized here — this README is a portfolio entry, not a tutorial.

what this repo demonstrates:
- End-to-end ML demo + explainability, pragmatic engineering for robustness, CI coverage for safety, and clear trade-offs documented in code and README.

Next steps I recommend (pick one)
- Add a short GIF (10–15s) of the Background Remover for the GitHub preview.  
- Add one small exemplar dataset and a single-click "Populate examples" button in the Binary Explorer.  
- Add CI badge and a short PR changelog for easier reviewer onboarding.

Where to look in git (quick commands)
- Recent commits: `git log -n 8 --oneline`  
- Show staged/unpushed changes: `git status --porcelain`  
- Get the HEAD sha to reference in your portfolio: `git rev-parse --short HEAD`

Contact / links
- Live demo: https://YOUR-WEBSITE.example.com  
- Replace the demo URL above with your public profile (LinkedIn / personal site) for recruiter-facing shares.

License
- MIT — suitable for demos and portfolio use.

---
