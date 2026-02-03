# Defensive guard: prevent Streamlit's file-watcher from probing `torch.classes` which
# can raise noisy runtime errors when introspected. This must run before
# importing Streamlit so the watcher doesn't trigger the proxy during startup.
try:
    import torch
    if hasattr(torch, "classes") and hasattr(torch.classes, "__path__"):
        torch.classes.__path__ = []
except Exception:
    # best-effort; don't fail app startup if torch is missing or behaves oddly
    pass

import streamlit as st

st.set_page_config(page_title="My Streamlit App", layout="centered")


# --- PAGE SETUP ---

about_page = st.Page(
    title="About me",
    page="pages/about_me.py",
    icon=":material/account_circle:",
    default=True,
)

project_1_page = st.Page(
    title="House Loan Calculator",
    page="pages/house_loan_calculator.py",
    icon=":material/bar_chart:"
)

project_2_page = st.Page(
    title="YOLO v11 Segmentation Model",
    page="pages/segmentation_model.py",
    icon=":material/smart_toy:"
)

background_remover_page = st.Page(
    title="Background Remover",
    page="pages/background_removal.py",
    icon="✂"
)

binary_explorer = st.Page(
    title="Binary Classification Explorer",
    page="pages/binary_classification.py",
    icon="📊"
)

# Chatbot page removed from navigation (kept in repo as an archived implementation).

# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
def _sanitize_page_text(s: str) -> str:
    """Remove characters that commonly cause Streamlit emoji/icon validation errors.
    This is conservative and only used as a runtime fallback so the app can start.
    """
    if not isinstance(s, str):
        return s
    # Remove characters in high emoji ranges (basic heuristic)
    return ''.join(ch for ch in s if ord(ch) < 0x1F300)

def _sanitize_page(p):
    try:
        if hasattr(p, 'title'):
            p.title = _sanitize_page_text(p.title)
        if hasattr(p, 'icon') and isinstance(p.icon, str) and len(p.icon) != 1:
            # only keep single-character icons
            p.icon = None
    except Exception:
        pass

try:
    pg = st.navigation(
        {
            "Info": [about_page],
            "Projects": [project_1_page, project_2_page, background_remover_page, binary_explorer],
        }
    )
except Exception as _err:
    # Attempt a conservative sanitization of page titles/icons and retry so the
    # app doesn't fail at startup due to an invalid emoji in page metadata.
    for candidate in (about_page, project_1_page, project_2_page, background_remover_page, binary_explorer):
        _sanitize_page(candidate)
    st.sidebar.warning("Invalid emoji detected in page metadata — removed to allow the app to start.")
    pg = st.navigation(
        {
            "Info": [about_page],
            "Projects": [project_1_page, project_2_page, background_remover_page, binary_explorer],
        }
    )

# --- SHARED ON ALL PAGES ---
from PIL import Image
img = Image.open("assets/profile_image.png")
st.logo(img)
st.sidebar.text("Made by Mahmoud Tabikh")

# --- Developer tools (visible in sidebar) -------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### Developer tools ⚙️")

def _clear_streamlit_caches():
    """Attempt multiple cache-clear APIs to free cached models/data."""
    results = []
    try:
        # Streamlit public API (may exist)
        st.cache_data.clear()
        results.append("cache_data")
    except Exception:
        pass
    try:
        st.cache_resource.clear()
        results.append("cache_resource")
    except Exception:
        pass
    try:
        # internal runtime API (best-effort)
        from streamlit.runtime.caching import clear_cache as _clear_cache
        _clear_cache()
        results.append("runtime.clear_cache")
    except Exception:
        pass
    return results

if st.sidebar.button("Clear caches and restart", help="Clears Streamlit caches (if available) and reloads the app"):
    cleared = _clear_streamlit_caches()
    if cleared:
        st.sidebar.success("Cleared: " + ", ".join(cleared))
    else:
        st.sidebar.info("No cache-clearing API available in this Streamlit version.")
    # Also clear session state keys that commonly hold widget blobs to avoid
    # deserialization errors caused by stale widget state from previous runs.
    for k in list(st.session_state.keys()):
        if any(prefix in k for prefix in ("seg_upload", "bg_upload", "bgimg", "bg_bgimg")):
            del st.session_state[k]
    st.experimental_rerun()

if st.sidebar.button("Show secrets file path"):
    import os
    possible = [os.path.expanduser("~/.streamlit/secrets.toml"), 
                os.path.abspath('.streamlit/secrets.toml'),
                os.path.join(os.getcwd(), '.streamlit', 'secrets.toml')]
    existing = [p for p in possible if os.path.exists(p)]
    if existing:
        st.sidebar.success("Found: " + existing[0])
    else:
        st.sidebar.warning("No secrets.toml found in common locations. See README.md/.streamlit/secrets.toml.example")

# quick helper to simulate missing-secrets behavior for testing
if st.sidebar.checkbox("Simulate missing secrets (for testing)"):
    st.session_state._simulate_missing_secrets = True

# --- RUN NAVIGATION ---
pg.run()
