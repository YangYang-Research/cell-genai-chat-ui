import streamlit as st
from helpers.config import AppConfig

class App:
    def __init__(self):
        self.config = AppConfig()

    def logout(self):
        st.logout()

    def run(self):
        st.logo(self.config.logo_path, size="large", icon_image=self.config.logo_path)

        st.set_page_config(
            page_title=self.config.page_title,
            page_icon=self.config.favicon_path,
            layout="wide",
        )
        
        pages = {
            "Cell": [
                st.Page("pages/home.py", title="Home", icon="⭐", url_path="/"),
                st.Page("pages/agent.py", title="Cell Agent", icon="🔮", url_path="/cell-agent"),
            ],
            "Account": [
                st.Page(self.logout, title="Logout", icon="🚪"),
            ],
        }

        pg = st.navigation(pages, position="top")
        pg.run()

def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()
