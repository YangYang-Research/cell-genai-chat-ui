import streamlit as st
from helpers.loog import logger

class BlankPage:
    def __init__(self):
        pass

    def display(self):
        st.title("Blank Page")
        st.write("This is a blank page. You can add your content here.")

    def run(self):
        self.display()

def main():
    try:
        page = BlankPage()
        page.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error("An unexpected error occurred. Please refresh the page and try again.")
        st.exception(e)

if __name__ == "__main__":
    main()