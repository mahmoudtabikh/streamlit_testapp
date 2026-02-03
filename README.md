# Streamlit Test App

A small demo Streamlit app with examples: an Open‑source LLM chatbot and an image background-removal tool (YOLOv8 segmentation). 

🔗 Local app URL (development):

- http://localhost:8501

(Use the **sidebar** to navigate pages or append a page query, e.g. `?page=Background%20Remover` — URL-encoding may be required.)

---

## Quick start (Windows)

1. Create & activate a virtualenv (recommended):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Run the app:

   ```powershell
   streamlit run streamlit_app.py
   ```

4. Open the app in your browser at: `http://localhost:8501` ✅

---

## Pages / features ✨

- `Background Remover` (pages/background_removal.py)
  - Remove image backgrounds using the included `yolov8n-seg.pt` segmentation model
  - Refine mask (dilate/erode/feather), replace with solid/image background, and download PNG with alpha

- `Chatbot` (pages/chat_bot.py)
  - Open-source LLM frontend with **Dev Mode** (runs small local models like `distilgpt2` for offline/dev use)
  - Supports streaming (token-by-token) when your `transformers` version provides `TextIteratorStreamer`

- Other pages: `About Me`, utilities, and examples.

---

## Important files

- `streamlit_app.py` — app entrypoint
- `pages/` — Streamlit multipage app source files
- `yolov8n-seg.pt` — YOLOv8 segmentation weights (checked into this workspace)
- `requirements.txt` — Python dependencies

---

## Secrets & credentials

To use the full (production) chatbot with hosted HF models, add your Hugging Face token to Streamlit secrets:

Create `.streamlit/secrets.toml` with:

```toml
HUGGING_FACE_API_KEY = "hf_...your_token..."
```

- Without a token, the app auto-enables **Dev Mode** so you can still test locally.

---

## Common troubleshooting ⚠️

- "Transformer/streaming not available": upgrade `transformers` to a newer release that exposes `TextIteratorStreamer` or disable streaming in the UI.
- "CUDA / OOM errors": try Dev Mode (small models) or run on a GPU; large models may be slow or fail on CPU.
- "Segmentation masks not extracted": ensure `ultralytics` matches the code API; the app expects `res.masks.data` or a numpy-compatible mask array.

---

## Running on a different port / host

```powershell
streamlit run streamlit_app.py --server.port 8502 --server.address 0.0.0.0
```

---

## Deployment (quick notes)

- Streamlit Cloud: push to a connected GitHub repo and set the `STREAMLIT_SERVER_PORT` / secrets in the app settings.
- Docker: build a container from this repo and expose port `8501`.

---

## Tests & developer tips

- Use **Dev Mode** in the Chatbot page for fast iteration without large downloads.  
- Background remover uses the checked-in `yolov8n-seg.pt` by default — replace with a different model by editing the page or dropping new weights in the project root.

---

If you want, I can: add a GitHub Actions workflow to auto-deploy to Streamlit Cloud, add a tiny pre-cached dev-model for fully offline testing, or create a short demo GIF. Which would you like next? 🎯