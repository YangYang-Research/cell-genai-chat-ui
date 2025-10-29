import requests
import streamlit as st
from helpers.loog import logger
from helpers.secret import AWSSecretManager
from helpers.utils import Utils
from helpers.config import AppConfig, AWSConfig, ChatConfig

class MakeRequest(object):
    def __init__(self, app_conf: AppConfig, aws_conf: AWSConfig, chat_conf: ChatConfig):
        self.app_conf = app_conf
        self.aws_conf = aws_conf
        self.chat_conf = chat_conf
        self.aws_secret_manager = AWSSecretManager(app_conf, aws_conf)

    def stream_chat_completions(self, chat_model: str, history: dict, prompt: str, attachments: list):
        """
        Stream tokens from backend API (StreamingResponse).
        """

        messages = []

        if chat_model == "claude":
            messages = [
                    {"role": "user" if m.type == "human" else "assistant", "content": m.content}
                    for m in history.messages
                ]
        
            if attachments:
                for attachment in attachments:
                    if attachment.status.value == "completed":
                        if attachment.is_image and attachment.base64:
                            messages = messages + [
                                {
                                    "role": "user", 
                                    "content": [
                                        {
                                            "type": "text", 
                                            "text": prompt
                                        },
                                        {
                                            "type": "image",
                                            "source": {
                                                "type": "base64",
                                                "media_type": attachment.type,
                                                "data": attachment.base64,
                                            },
                                        },
                                    ]
                                }
                            ]
                        elif attachment.is_document and attachment.base64:
                            messages = messages + [
                                {
                                    "role": "user", 
                                    "content": [
                                        {
                                            "type": "text", 
                                            "text": prompt
                                        },
                                        {
                                            "document": {
                                                # Available formats: html, md, pdf, doc/docx, xls/xlsx, csv, and txt
                                                "format": Utils.get_file_format(attachment.type),
                                                "name": Utils.format_filename(attachment.name),
                                                "source": {"bytes": attachment.base64}, #(convert bytes → base64 string) for sending over HTTP
                                            }
                                        },
                                    ]
                                }
                            ]
                        elif attachment.is_text and attachment.content:
                            messages = messages + [
                                {
                                    "role": "user", 
                                    "content": [
                                        {
                                            "type": "text", 
                                            "text": prompt
                                        },
                                        {
                                            "type": "text", 
                                            "text": attachment.content
                                        },
                                    ]
                                }
                            ]
                        else:
                            pass
            else:
                messages = messages + [{"role": "user", "content": prompt}]
        else:
            st.toast(f"Model : {chat_model} currently not supported", icon="⚠️")
            st.stop()

        if isinstance(messages, tuple):
            messages = list(messages)

        payload = {
            "chat_session_id": "123",
            "model_name": chat_model,
            "messages": messages,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.aws_secret_manager.get_secret(self.chat_conf.chat_auth_key_name)}",
        }

        try:
            with requests.post(self.chat_conf.chat_service_api + self.chat_conf.chat_agent_completions_endpoint, headers=headers, json=payload, stream=True, timeout=self.chat_conf.chat_timeout_seconds) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=None):
                    if chunk:
                        yield chunk.decode("utf-8")
        except requests.exceptions.RequestException as e:
            logger.error(f"[FE-CHAT_SERVICE] Stream error: {e}")
            yield f"\n[Error] Unable connect to chat service. Please try again."
    
    def post(self, endpoint: str, data: dict):
        """
        Send a POST request to the specified endpoint with the given data.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.aws_secret_manager.get_secret(self.chat_conf.chat_auth_key_name)}",
        }
        try:
            response = requests.post(self.chat_conf.chat_service_api + endpoint, headers=headers, json=data, timeout=self.chat_conf.chat_timeout_seconds)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"[FE-CHAT_SERVICE] POST error: {e}")
            yield f"\n[Error] Unable connect to chat service. Please try again."
            