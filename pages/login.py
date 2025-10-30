import streamlit as st
import uuid
import base64
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from helpers.config import AppConfig
from helpers.loog import logger

with open('auth_config.yml') as file:
    config = yaml.load(file, Loader=SafeLoader)

stauth.Hasher.hash_passwords(config['credentials'])
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# ------------- Login Page Class -------------
class LoginPage:
    def __init__(self):
        self.app_conf = AppConfig()

    def display(self):
        st.logo(self.app_conf.logo_path, size="large", icon_image=self.app_conf.logo_path)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            base64_logo = base64.b64encode(open(self.app_conf.logo_path, "rb").read()).decode("utf-8")
            st.markdown(
                f"""
                <div style="text-align: left;">
                    <h2><img src="data:image/png;base64,{base64_logo}" alt="Logo" style="width: 100px;"/>{self.app_conf.app_name}</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )

            authenticator.login()

            if st.session_state.get("authentication_status"):
                st.success("Login successful!")
                st.session_state["chat_session_id"] = uuid.uuid1()
                st.rerun()
            elif st.session_state.get("authentication_status") is False:
                st.error("Username/password is incorrect")
            else:
                st.info("Please enter your username and password")

    def run(self):
        self.display()
    
def main():
    try:
        page = LoginPage()
        page.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error("An unexpected error occurred. Please refresh the page and try again.")
        st.exception(e)

if __name__ == "__main__":
    main()