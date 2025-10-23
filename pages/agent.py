import streamlit as st
from helpers.loog import logger
from helpers.utils import Utils
from helpers.http import CellHTTP
from helpers.config import AppConfig, AWSConfig, ChatConfig
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

app_config = AppConfig()
aws_config = AWSConfig()
chat_config = ChatConfig()
cell_http = CellHTTP(app_config, aws_config, chat_config)
utils = Utils()

def init_feedback_state():
    """Initialize feedback tracking in session state."""
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}  # {message_index: "up"/"down"}

def save_feedback(message_index: int):
    """Save user feedback and send to backend."""
    key = f"feedback_{message_index}"
    user_feedback = st.session_state.get(key, None)

    if "feedback" not in st.session_state:
        st.session_state.feedback = {}
    st.session_state.feedback[message_index] = user_feedback

    # Retrieve message content (safe lookup)
    msgs = st.session_state.get("chat_history", None)
    if isinstance(msgs, list):
        if 0 <= message_index < len(msgs):
            message_content = getattr(msgs[message_index], "content", None)
    elif hasattr(msgs, "messages"):
        all_msgs = getattr(msgs, "messages", [])
        if 0 <= message_index < len(all_msgs):
            message_content = getattr(all_msgs[message_index], "content", None)
    
    logger.info(f"[Feedback] Message {message_index} => {user_feedback}")
    try:
        if message_content:
            cell_http.post_request(
                endpoint=chat_config.chat_feedback_endpoint,
                data={
                    "message_index": message_index,
                    "message_content": message_content,
                    "feedback": user_feedback,
                },
            )
        else:
            logger.warning(f"[Feedback] No content found for message {message_index}")
    except Exception as e:
        logger.error(f"[Feedback] Failed to send feedback: {e}")

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

            # Feedback for assistant messages only
            if role == "assistant":
                existing_feedback = st.session_state.feedback.get(idx)
                st.session_state[f"feedback_{idx}"] = existing_feedback
                st.feedback(
                    "thumbs",
                    key=f"feedback_{idx}",
                    disabled=existing_feedback is not None,
                    on_change=save_feedback,
                    args=[idx],
                )

        # Input box
        if message := st.chat_input("Type your message here...", accept_file="multiple", file_type=["txt", "pdf", "docx", "png", "jpg", "jpeg", "csv", "xlsx"]):

            prompt = message["text"]
            files = message["files"]
            attachments = []
            
            if not prompt:
                st.warning("Please enter a message.")
                st.stop()
            
            if files:
                attachments = utils.process_multiple_files(files)
            
            msgs.add_user_message(prompt)
            st.chat_message("user").write(prompt)

            if files:
                for attachment in attachments:
                    if attachment.is_image:
                        st.image(image=attachment.bytes, width=100)
                        st.write(f"Attachment: {attachment.name} - {attachment.size_kb} KB")
                    else:
                        st.write(f"Attachment: {attachment.name} - {attachment.size_kb} KB")

            # Stream AI response
            with st.chat_message("assistant"):
                placeholder = st.empty()
                full_response = ""
                for chunk in cell_http.stream_chat_completions(prompt, msgs, attachments):
                    full_response += chunk
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)

                msgs.add_ai_message(full_response)
                
                # Feedback for new AI message
                idx = len(msgs.messages) - 1
                st.session_state[f"feedback_{idx}"] = None
                st.feedback(
                    "thumbs",
                    key=f"feedback_{idx}",
                    on_change=save_feedback,
                    args=[idx],
                )

    def run(self):
        self.display()

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
