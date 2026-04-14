# ===========================================
# Author:      Sushant Kakkeri
# Title:       Senior Enterprise Software
#              Engineer
# Application: MCP Research Assistant
# Created:     April 2026
# Copyright:   © 2026 Sushant Kakkeri
#              All Rights Reserved
# ===========================================

import streamlit as st
from dotenv import load_dotenv
from rag_tool import RAGTool
from mcp_agent import MCPAgent
import os

load_dotenv()

# ===========================================
# PAGE CONFIGURATION
# ===========================================
st.set_page_config(
    page_title="MCP Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===========================================
# CUSTOM STYLING
# ===========================================
st.markdown("""
<style>
.step-box {
    background: #f0f7ff;
    border-left: 3px solid #2196F3;
    padding: 8px 12px;
    margin: 4px 0;
    border-radius: 4px;
    font-family: monospace;
    font-size: 13px;
}
.tool-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 12px;
    font-weight: bold;
    margin: 2px;
}
.author-bar {
    background: linear-gradient(
        90deg, #1a1a2e, #16213e);
    padding: 8px 15px;
    border-radius: 8px;
    margin-bottom: 10px;
}
.footer-bar {
    text-align: center;
    padding: 15px;
    background: linear-gradient(
        90deg, #1a1a2e, #16213e);
    border-radius: 10px;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# ===========================================
# SIDEBAR
# ===========================================
st.sidebar.title("🔬 Research Assistant")
st.sidebar.caption(
    "MCP makes ALL decisions automatically!")
st.sidebar.markdown("---")

# API Key input
openai_key = st.sidebar.text_input(
    "🔑 OpenAI API Key",
    value=os.getenv("OPENAI_API_KEY", ""),
    type="password")

if openai_key:

    if "rag_tool" not in st.session_state:
        st.session_state.rag_tool = (
            RAGTool(openai_key))
        st.session_state.mcp_agent = (
            MCPAgent(
                openai_key,
                st.session_state.rag_tool))
        st.session_state.messages = []

    st.sidebar.markdown("---")

    # PDF Upload
    st.sidebar.subheader(
        "📄 Upload Documents (Optional)")
    st.sidebar.caption(
        "MCP searches these automatically!")

    uploaded_files = st.sidebar.file_uploader(
        "Upload PDFs",
        type="pdf",
        accept_multiple_files=True)

    if uploaded_files:
        for f in uploaded_files:
            key = f"loaded_{f.name}"
            if key not in st.session_state:
                with st.spinner(
                        f"📚 Indexing {f.name}"):
                    success, info = (
                        st.session_state
                        .rag_tool.load_pdf(f))
                    if success:
                        st.session_state[
                            key] = True
                        st.sidebar.success(
                            f"✅ {f.name} "
                            f"({info} chunks)")
                    else:
                        st.sidebar.error(
                            f"❌ {info}")

    st.sidebar.markdown("---")

    # Tool Status
    st.sidebar.subheader("🤖 MCP Tools Ready")

    tools_list = [
        "🌐 Web Search",
        "📖 Wikipedia",
        "📰 News Search",
        "📊 Report Generator",
        "💾 Report Saver",
        "🕐 Date & Time"
    ]

    if (st.session_state.rag_tool
            .has_documents()):
        tools_list.insert(0, "📄 Doc Search ✅")
        files = (st.session_state.rag_tool
                 .get_loaded_files())
        st.sidebar.success(
            f"📄 {len(files)} doc(s) loaded!")
    else:
        tools_list.insert(
            0, "📄 Doc Search (no docs)")
        st.sidebar.info("Upload PDFs to enable!")

    for tool in tools_list:
        st.sidebar.caption(f"  • {tool}")

    st.sidebar.markdown("---")

    # Clear button
    if st.sidebar.button(
            "🗑️ Clear Conversation",
            use_container_width=True):
        st.session_state.messages = []
        st.session_state.mcp_agent\
            .clear_history()
        st.rerun()

    # ─────────────────────────────
    # SIDEBAR AUTHOR SIGNATURE
    # ─────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
<div style='text-align: center;
    padding: 10px;'>
    <div style='color: #e94560;
        font-weight: bold;
        font-size: 13px;'>
        👨‍💻 Sushant Kakkeri
    </div>
    <div style='color: gray;
        font-size: 11px;
        margin-top: 4px;'>
        Senior Enterprise Software Engineer
    </div>
    <div style='color: gray;
        font-size: 10px;
        margin-top: 2px;'>
        © 2026 All Rights Reserved
    </div>
</div>
""", unsafe_allow_html=True)

# ===========================================
# MAIN INTERFACE
# ===========================================
st.title("🔬 MCP Research Assistant")

# ─────────────────────────────
# AUTHOR BAR UNDER TITLE
# ─────────────────────────────
st.markdown("""
<div class='author-bar'>
    <span style='color: #e94560;
        font-weight: bold;
        font-size: 13px;'>
        👨‍💻 Built by Sushant Kakkeri
    </span>
    <span style='color: #aaa;
        font-size: 12px;'>
        &nbsp;|&nbsp;
        Senior Enterprise Software Engineer
        &nbsp;|&nbsp;
        © 2026 All Rights Reserved
    </span>
</div>
""", unsafe_allow_html=True)

st.caption(
    "MCP AI Agent — decides which tools "
    "to use, in what order, automatically!")

# How it works explainer
with st.expander(
        "🧠 How MCP Makes Decisions"):
    col1, col2, col3 = st.columns(3)
    col1.markdown("""
    ### 📋 Step 1: Understand
    MCP reads your question and
    plans its own research strategy.
    No router tells it what to do!
    """)
    col2.markdown("""
    ### 🔧 Step 2: Research
    MCP calls multiple tools in
    sequence automatically.
    Wikipedia + Web + Docs + News!
    """)
    col3.markdown("""
    ### 📊 Step 3: Report
    MCP compiles all findings into
    a structured report and saves
    to file if you ask!
    """)

st.markdown("---")

if openai_key:

    # Demo Question Buttons
    st.subheader("💡 Try These Demo Questions")
    col1, col2, col3 = st.columns(3)

    q1 = col1.button(
        "🌍 Research AI developments",
        use_container_width=True)
    q2 = col2.button(
        "🚀 Research Mars + my documents",
        use_container_width=True)
    q3 = col3.button(
        "📊 Quantum computing full report",
        use_container_width=True)

    st.markdown("---")

    # Tool colors
    TOOL_COLORS = {
        "web_search": "#4CAF50",
        "wikipedia_search": "#2196F3",
        "news_search": "#FF9800",
        "search_documents": "#9C27B0",
        "generate_report": "#F44336",
        "save_report": "#795548",
        "get_current_datetime": "#607D8B"
    }

    # Chat history display
    for msg in st.session_state.get(
            "messages", []):
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            with st.chat_message(
                    "assistant",
                    avatar="🔬"):
                if msg.get("tools_used"):
                    st.markdown(
                        "**🤖 MCP Used:**")
                    badges = ""
                    for tool in (
                            msg["tools_used"]):
                        color = TOOL_COLORS.get(
                            tool, "#999")
                        badges += (
                            f'<span class='
                            f'"tool-badge" '
                            f'style="background:'
                            f'{color};color:white">'
                            f'{tool}</span> ')
                    st.markdown(
                        badges,
                        unsafe_allow_html=True)

                if msg.get("steps"):
                    with st.expander(
                            f"🔍 MCP Research "
                            f"Steps "
                            f"({len(msg['steps'])"
                            f"})"):
                        for step in msg["steps"]:
                            st.markdown(
                                f'<div class='
                                f'"step-box">'
                                f'{step}</div>',
                                unsafe_allow_html
                                =True)

                st.write(msg["content"])

    # Chat input
    user_input = st.chat_input(
        "Ask me to research anything — "
        "MCP decides how to find it!")

    # Demo button handlers
    if q1:
        user_input = (
            "Research the latest developments "
            "in artificial intelligence. "
            "Use web search, Wikipedia and "
            "news search for comprehensive info.")
    if q2:
        user_input = (
            "Research Mars exploration — "
            "search my uploaded documents "
            "AND find latest mission news "
            "AND Wikipedia background info.")
    if q3:
        user_input = (
            "Research quantum computing "
            "thoroughly. Use all available tools. "
            "Then generate a complete structured "
            "report and save it to a file.")

    # Process input
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)

        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message(
                "assistant",
                avatar="🔬"):
            with st.spinner(
                    "🤖 MCP researching — "
                    "deciding tools to use..."):
                result = (
                    st.session_state
                    .mcp_agent.research(
                        user_input))

            if result["tools_used"]:
                st.markdown(
                    "**🤖 MCP Automatically "
                    "Used:**")
                badges = ""
                for tool in result["tools_used"]:
                    color = TOOL_COLORS.get(
                        tool, "#999")
                    badges += (
                        f'<span class="tool-badge"'
                        f' style="background:'
                        f'{color};color:white">'
                        f'{tool}</span> ')
                st.markdown(
                    badges,
                    unsafe_allow_html=True)

            if result["steps"]:
                with st.expander(
                        f"🔍 MCP Research Steps "
                        f"({len(result['steps'])"
                        f"})"):
                    for step in result["steps"]:
                        st.markdown(
                            f'<div class='
                            f'"step-box">'
                            f'{step}</div>',
                            unsafe_allow_html=True)

            st.write(result["answer"])

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "tools_used": result["tools_used"],
            "steps": result["steps"]
        })

else:
    st.warning(
        "👈 Enter your OpenAI API key "
        "in the sidebar to start!")
    st.info(
        "MCP Research Assistant:\n\n"
        "• MCP decides which tools to use\n"
        "• No router needed\n"
        "• Uses web, Wikipedia, news, docs\n"
        "• Generates and saves reports!\n"
        "• True AI Agent behavior!")

# ─────────────────────────────
# FOOTER
# ─────────────────────────────
st.markdown("---")
st.markdown("""
<div class='footer-bar'>
    <div style='color: #e94560;
        font-weight: bold;
        font-size: 14px;'>
        🔬 MCP Research Assistant
    </div>
    <div style='color: #aaa;
        font-size: 12px;
        margin-top: 5px;'>
        Built by
        <b style='color: white;'>
            Sushant Kakkeri
        </b>
        &nbsp;|&nbsp;
        Senior Enterprise Software Engineer
    </div>
    <div style='color: gray;
        font-size: 11px;
        margin-top: 4px;'>
        Powered by OpenAI GPT-4o +
        LangChain + FAISS + Streamlit
        &nbsp;|&nbsp;
        © 2026 All Rights Reserved
    </div>
</div>
""", unsafe_allow_html=True)