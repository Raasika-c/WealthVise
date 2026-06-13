# pages/3_Chatbot.py — WealthVise Groq LLaMA 3 Chatbot
# M4 owns this file.

# Third-party
import streamlit as st

# Internal
from config import DISCLAIMER, GROQ_API_KEY

# ── Session guard ─────────────────────────────────────────────────────────────
if "username" not in st.session_state:
    st.warning("Please log in from the home page.")
    st.stop()

# ── Page layout ───────────────────────────────────────────────────────────────
st.title("💬 WealthVise Chatbot")
st.caption("Powered by Groq LLaMA 3 — ask anything about investing.")

# ── Chat history ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ── Clear chat button ─────────────────────────────────────────────────────────
if st.button("🗑️ Clear Chat"):
    st.session_state["chat_history"] = []
    st.rerun()

# ── Render history ────────────────────────────────────────────────────────────
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask a question about stocks or investing…")

if user_input:
    # Append user message
    st.session_state["chat_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call Groq
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                if not GROQ_API_KEY:
                    raise ValueError("GROQ_API_KEY is not set. Add it to .env or st.secrets.")

                from groq import Groq

                client = Groq(api_key=GROQ_API_KEY)

                system_prompt = (
                    "You are WealthVise, an AI investment assistant. "
                    "You provide clear, educational explanations about stocks, investing, "
                    "and financial concepts. You do not give personalised financial advice. "
                    f"{DISCLAIMER}"
                )

                messages_payload = [{"role": "system", "content": system_prompt}]
                # Include last 10 messages for context
                messages_payload += st.session_state["chat_history"][-10:]

                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=messages_payload,
                    max_tokens=1024,
                    temperature=0.7,
                )
                answer = response.choices[0].message.content

            except Exception as exc:
                answer = f"⚠️ Could not reach Groq API: {exc}"

        st.markdown(answer)
        st.session_state["chat_history"].append({"role": "assistant", "content": answer})

st.divider()
st.caption(DISCLAIMER)
