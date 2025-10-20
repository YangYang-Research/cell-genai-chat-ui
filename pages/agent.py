import streamlit as st
import requests
from helpers.loog import logger
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

# ===========================
# Backend API Configuration
# ===========================
API_URL = "http://localhost:8000/chat/stream"  # Update to your deployed BE URL

# ===========================
# Utility: Stream API response
# ===========================
def stream_chat_response(prompt, history, model_cfg):
    """
    Stream tokens from backend API (StreamingResponse).
    """
    payload = {
        "model_id": model_cfg.get("model_id", "anthropic.claude-3-sonnet-20240229-v1:0"),
        "temperature": model_cfg.get("temperature", 0.7),
        "max_tokens": model_cfg.get("max_tokens", 512),
        "messages": [
            {"role": "user" if m.type == "human" else "assistant", "content": m.content}
            for m in history.messages
        ] + [{"role": "user", "content": prompt}],
    }

    try:
        with requests.post(API_URL, json=payload, stream=True, timeout=300) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=None):
                if chunk:
                    yield chunk.decode("utf-8")
    except requests.exceptions.RequestException as e:
        logger.error(f"[FE] Stream error: {e}")
        yield f"\n[Error] Unable to reach backend service: {e}"


# ===========================
# Feedback Handling
# ===========================
def init_feedback_state():
    """Initialize feedback tracking in session state."""
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}  # {message_index: "up"/"down"}

def save_feedback(message_index, value):
    """Save user feedback."""
    st.session_state.feedback[message_index] = value
    logger.info(f"[Feedback] Message {message_index} feedback: {value}")


# ===========================
# Streamlit App Class
# ===========================
class AgentPage:
    def __init__(self):
        self.model_cfg = {
            "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
            "temperature": 0.7,
            "max_tokens": 512,
        }

    def display(self):
        st.title("🧠 Cell GenAI Chat UI")
        st.caption("Lightweight streaming GenAI chat powered by AWS Bedrock + LangChain")

        # Initialize feedback store
        init_feedback_state()

        msgs = StreamlitChatMessageHistory(key="chat_history")
        if not msgs.messages:
            msgs.add_ai_message("👋 Hello! How can I assist you today?")

        # Display chat history
        for idx, msg in enumerate(msgs.messages):
            role = "assistant" if msg.type == "ai" else "user"
            st.chat_message(role).write(msg.content)

            # Add feedback for assistant messages only
            if role == "assistant":
                st.feedback(
                    "thumbs",
                    key=f"feedback_{idx}",
                    on_change=save_feedback,
                    args=[idx],
                )

        # Input box
        if prompt := st.chat_input("Type your message here..."):
            msgs.add_user_message(prompt)
            st.chat_message("user").write(prompt)

            # Stream AI response
            with st.chat_message("assistant"):
                placeholder = st.empty()
                full_response = ""
                for chunk in stream_chat_response(prompt, msgs, self.model_cfg):
                    full_response += chunk
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                msgs.add_ai_message(full_response)

                # Add feedback component
                st.feedback(
                    "thumbs",
                    key=f"feedback_{len(msgs.messages)}",
                    on_change=save_feedback,
                    args=[len(msgs.messages)],
                )

    def run(self):
        self.display()


# ===========================
# Main Entrypoint
# ===========================
def main():
    try:
        page = AgentPage()
        page.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error("An unexpected error occurred. Please refresh and try again.")
        st.exception(e)


if __name__ == "__main__":
    main()
