import streamlit as st
from helpers.loog import logger
from helpers.http import CellHTTP
from helpers.config import AppConfig, AWSConfig, ChatConfig
from langchain_community.chat_message_histories import StreamlitChatMessageHistory


cell_http = CellHTTP(AppConfig(), AWSConfig(), ChatConfig())

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
        pass

    def display(self):
        st.title("🔮 Cell")
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
                for chunk in cell_http.stream_chat_request(prompt, msgs):
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
