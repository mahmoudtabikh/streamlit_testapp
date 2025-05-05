import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

torch.classes.__path__ = [] # add this line to manually set it to empty. 
hf_token = st.secrets["HUGGING_FACE_API_KEY"]

@st.cache_resource
def load_model():
    model_name = "tiiuae/falcon-rw-1b"
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        token=hf_token
    )
    return model, tokenizer

model, tokenizer = load_model()

st.title("🤖 Open Source Chatbot")
st.markdown("Ask me anything. Powered by an open-source LLM.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("You:", "")

def generate_response(prompt):
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(model.device)
    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_new_tokens=256,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    decoded = tokenizer.decode(output[0], skip_special_tokens=True)
    return decoded[len(prompt):].strip()

if user_input:
    st.session_state.chat_history.append(("You", user_input))
    full_prompt = "\n".join([f"{u}: {t}" for u, t in st.session_state.chat_history])
    bot_response = generate_response(full_prompt)
    st.session_state.chat_history.append(("Bot", bot_response))

for sender, text in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"**🧑‍💬 {sender}:** {text}")
    else:
        st.markdown(f"**🤖 {sender}:** {text}")
