import streamlit as st
from helpers.config import ToolInfo, ToolDescription
from helpers.loog import logger

class HomePage:
    def __init__(self):
        self.tools = sorted(
            [
                ToolInfo(
                    name=name,
                    description=data["description"],
                    tags=data["tags"],
                    logo=data["logo"],
                )
                for name, data in ToolDescription.DATA.items()
            ],
            key=lambda t: t.name.lower(),
        )

    def display(self):
        st.title("🚀 Cell - GenAI Chat UI")

        st.markdown("### 🧩 Agent Tools")

        cols = st.columns(4)
        for i, tool in enumerate(self.tools):
            col = cols[i % 4]
            with col:
                self.render_tool_card(tool)
        
    
    def render_tool_card(self, tool: ToolInfo):
        """Renders each tool in a card format with click behavior."""
        card_key = f"tool_{tool.name}"

        with st.container():
            st.markdown(
            f"""
            <div style="
                border-radius: 12px;
                padding: 15px;
                margin: 8px 0;
                background-color: #f9f9f9;
                box-shadow: 0 1px 4px rgba(0,0,0,0.1);
                cursor: pointer;
                transition: 0.2s;
            "
                onmouseover="this.style.backgroundColor='#f0f0f0';"
                onmouseout="this.style.backgroundColor='#f9f9f9';"
            >
                <h4 style="margin-bottom:6px;">{tool.logo} {tool.name}</h4>
                <p style="font-size: 14px; margin-top: 0; color: #555;">{tool.description}</p>
                <div style="display:flex; flex-wrap:wrap; gap:4px;">
                    {''.join([
                        f'<span style="background-color:#e0f2ff;color:#007bff;padding:2px 8px;border-radius:8px;font-size:12px;">{tag}</span>'
                        for tag in tool.tags
                    ])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
    def run(self):
        self.display()

def main():
    try:
        page = HomePage()
        page.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error("An unexpected error occurred. Please refresh the page and try again.")
        st.exception(e)

if __name__ == "__main__":
    main()