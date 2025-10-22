import requests
from helpers.config import AppConfig, AWSConfig, ChatConfig
from helpers.secret import AWSSecretManager
from helpers.loog import logger

class CellHTTP:
    def __init__(self, app_conf: AppConfig, aws_conf: AWSConfig, chat_conf: ChatConfig):
        self.app_conf = app_conf
        self.aws_conf = aws_conf
        self.chat_conf = chat_conf
        self.aws_secret_manager = AWSSecretManager(app_conf, aws_conf)

    def stream_chat_completions(self, prompt: str, history: dict):
        """
        Stream tokens from backend API (StreamingResponse).
        """
        payload = {
            "model_id": self.chat_conf.chat_model_id,
            "temperature": self.chat_conf.temperature,
            "max_tokens": self.chat_conf.max_response_tokens,
            "messages": [
                {"role": "user" if m.type == "human" else "assistant", "content": m.content}
                for m in history.messages
            ] + [{"role": "user", "content": prompt}],
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.aws_secret_manager.get_secret(self.chat_conf.chat_auth_key_name)}",
        }

        try:
            with requests.post(self.chat_conf.chat_service_api + self.chat_conf.chat_completions_endpoint, headers=headers, json=payload, stream=True, timeout=self.chat_conf.chat_timeout_seconds) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=None):
                    if chunk:
                        yield chunk.decode("utf-8")
        except requests.exceptions.RequestException as e:
            logger.error(f"[FE-CHAT_SERVICE] Stream error: {e}")
            yield f"\n[Error] Unable connect to chat service. Please try again."
    
    def post_request(self, endpoint: str, data: dict):
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
            