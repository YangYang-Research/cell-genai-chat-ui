import streamlit as st
from helpers.loog import logger

class UserPage:
    def __init__(self):
        pass

    def display(self):
        st.title("User Information")
        st.markdown(f"#### Username: {st.session_state.get('username')}")
        st.markdown(f"#### Email: {st.session_state.get('email')}")
        st.markdown(f"#### Role: {st.session_state.get('roles')}")

    def run(self):
        self.display()

def main():
    try:
        page = UserPage()
        page.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error("An unexpected error occurred. Please refresh the page and try again.")
        st.exception(e)

if __name__ == "__main__":
    main()