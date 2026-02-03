import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import threading

# optional streaming helper (may not be present in older transformers)
try:
    from transformers import TextIteratorStreamer
    _STREAMER_AVAILABLE = True
except Exception:
    TextIteratorStreamer = None
    _STREAMER_AVAILABLE = False

torch.classes.__path__ = [] # add this line to manually set it to empty. 
# read HF token safely (may be absent in local/dev environments)
hf_token = st.secrets.get("HUGGING_FACE_API_KEY", None)

@st.cache_resource
def load_model(model_name: str = "tiiuae/falcon-rw-1b"):
    """Load model safely:
    - use `use_auth_token` (correct HF arg)
    - fall back to CPU when CUDA isn't available
    - provide clear error messages for missing credentials / OOMs
    """
    use_auth = hf_token if hf_token else None
    if use_auth is None:
        st.warning("Hugging Face API key not found in `st.secrets`. Public access may be rate-limited or fail.")

    try:
        has_cuda = torch.cuda.is_available()
        # choose dtype/device strategy
        if has_cuda:
            torch_dtype = torch.float16
            device_map = "auto"
            low_cpu_mem = False
        else:
            torch_dtype = torch.float32
            device_map = {"": "cpu"}
            low_cpu_mem = True

        with st.spinner(f"Loading {model_name} ({'GPU' if has_cuda else 'CPU'})..."):
            tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=use_auth)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch_dtype,
                device_map=device_map,
                low_cpu_mem_usage=low_cpu_mem,
                use_auth_token=use_auth
            )
    except Exception as e:
        st.error(f"Failed to load model '{model_name}': {e}")
        raise
    return model, tokenizer

# --- Dev-mode / model selection UI -------------------------------------------------
# If no HF token is available, enable a lightweight local model for fast dev/test.
default_dev = hf_token is None
dev_mode = st.checkbox("Dev mode — use a small local model for fast testing (no HF key required)", value=default_dev)

dev_model_option = st.selectbox(
    "Development model (small)",
    options=["distilgpt2", "sshleifer/tiny-gpt2"],
    index=0,
    help="Small models that run quickly on CPU for UI/dev testing"
)

# Choose model to load
if dev_mode:
    model_name = dev_model_option
else:
    model_name = "tiiuae/falcon-rw-1b"

# If user attempted prod without a token, switch to dev and inform them
if not dev_mode and hf_token is None:
    st.info("No Hugging Face API key found — switching to dev model for local testing.")
    dev_mode = True
    model_name = dev_model_option

# Attempt to load the chosen model, but automatically fall back to the dev model
# if the production model fails (avoids crashing the UI). The fallback is cached
# per-model because `load_model` accepts `model_name` and is decorated with
# `st.cache_resource`.
try:
    model, tokenizer = load_model(model_name)
except Exception as e:
    # If loading the requested model fails, try the dev model so the UI remains usable.
    st.warning(
        f"Failed to load model '{model_name}': {e}. Falling back to development model '{dev_model_option}' for testing."
    )
    try:
        model, tokenizer = load_model(dev_model_option)
        dev_mode = True
        model_name = dev_model_option
    except Exception as e2:
        # If fallback also fails, surface the error so the developer can debug.
        st.error(f"Failed to load fallback model '{dev_model_option}': {e2}")
        raise

st.title("🤖 Open Source Chatbot")
st.markdown("Ask me anything. Powered by an open-source LLM.")

if dev_mode:
    st.info(f"Running in **dev mode** with `{model_name}` — smaller, faster, and suitable for UI testing (not production-quality).")
# -------------------------------------------------------------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("You:", "")

def generate_response(prompt: str, max_new_tokens: int = 256, temperature: float = 0.7) -> str:
    """Non-streaming generation (token-aware) with device-safe retry."""
    enc = tokenizer(prompt, return_tensors="pt")
    device = next(model.parameters()).device
    input_ids = enc.input_ids.to(device)
    input_len = input_ids.shape[-1]

    with torch.no_grad():
        try:
            output = model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )
        except RuntimeError:
            st.warning("Generation failed on the current device — retrying on CPU (this may be slow).")
            model.to("cpu")
            input_ids = input_ids.to("cpu")
            output = model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )

    gen_tokens = output[0][input_len:]
    return tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()


def generate_response_stream(prompt: str, placeholder, max_new_tokens: int = 256, temperature: float = 0.7) -> str:
    """Stream tokens into `placeholder` using TextIteratorStreamer when available.
    - `placeholder` is an st.empty() container where partial text will be shown.
    - Falls back to `generate_response` when streaming isn't available or fails.
    """
    if not _STREAMER_AVAILABLE:
        placeholder.info("Streaming not available with installed transformers — falling back to non-streaming generation.")
        return generate_response(prompt, max_new_tokens=max_new_tokens, temperature=temperature)

    enc = tokenizer(prompt, return_tensors="pt")
    device = next(model.parameters()).device
    input_ids = enc.input_ids.to(device)

    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    # Start generate in a background thread
    gen_kwargs = dict(
        input_ids=input_ids,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=0.9,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
        streamer=streamer,
    )

    gen_thread = threading.Thread(target=model.generate, kwargs=gen_kwargs, daemon=True)
    gen_thread.start()

    # Consume streamer and update UI incrementally
    collected = []
    text_so_far = ""
    for chunk in streamer:
        collected.append(chunk)
        text_so_far = "".join(collected)
        # render progressive output (use markdown to preserve newlines)
        placeholder.markdown(text_so_far)

    # Ensure the generation thread finished
    gen_thread.join()
    return text_so_far.strip()

stream_responses = st.checkbox("Stream responses (token-by-token)", value=True, help="Show the model's output as it's generated for faster feedback on long responses.")

if user_input:
    st.session_state.chat_history.append(("You", user_input))
    full_prompt = "\n".join([f"{u}: {t}" for u, t in st.session_state.chat_history])

    # Placeholder for streaming output (visible immediately)
    placeholder = st.empty()

    if stream_responses and _STREAMER_AVAILABLE:
        try:
            bot_response = generate_response_stream(full_prompt, placeholder)
        except Exception as e:
            # If streaming fails, fall back to single-shot generation and show an error
            st.error(f"Streaming failed; falling back to standard generation: {e}")
            bot_response = generate_response(full_prompt)
            placeholder.markdown(bot_response)
    else:
        if stream_responses and not _STREAMER_AVAILABLE:
            st.info("Streaming not supported by the installed transformers package; using standard generation.")
        bot_response = generate_response(full_prompt)
        placeholder.markdown(bot_response)

    st.session_state.chat_history.append(("Bot", bot_response))

for sender, text in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"**🧑‍💬 {sender}:** {text}")
    else:
        st.markdown(f"**🤖 {sender}:** {text}")
