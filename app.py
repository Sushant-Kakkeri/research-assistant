# ===========================================
# app.py
# ===========================================
# The FRONT DOOR — what users see.
#
# KEY DIFFERENCE from previous app:
# Previous app.py = complex
# Had routing logic and decisions
#
# This app.py = SIMPLE
# Just shows UI and passes to MCP!
# ALL intelligence is in mcp_agent.py!
#
# App's only jobs:
# 1. Show the interface
# 2. Take user input
# 3. Pass to MCPAgent
# 4. Display results
# Nothing more!
# ===========================================

# Streamlit = turns Python into web app
import streamlit as st

# Load API key from .env file automatically
from dotenv import load_dotenv

# Our custom modules
from rag_tool import RAGTool    # RAG as tool
from mcp_agent import MCPAgent  # MCP brain

# Access environment variables
import os

# Load .env file at startup
load_dotenv()


# ===========================================
# PAGE CONFIGURATION
# ===========================================
# MUST be first Streamlit command!
# Sets browser tab, layout, sidebar
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
# CSS makes app look professional
# ===========================================
st.markdown("""
<style>
/* Research step display boxes */
/* Blue bordered - shows MCP thinking */
.step-box {
    background: #f0f7ff;
    border-left: 3px solid #2196F3;
    padding: 8px 12px;
    margin: 4px 0;
    border-radius: 4px;
    font-family: monospace;
    font-size: 13px;
}

/* Colored tool name labels */
/* Each tool gets its own color */
.tool-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 12px;
    font-weight: bold;
    margin: 2px;
}
</style>
""", unsafe_allow_html=True)


# ===========================================
# SIDEBAR
# ===========================================
# Left panel with settings and status
# ===========================================
st.sidebar.title("🔬 Research Assistant")
st.sidebar.caption(
    "MCP makes ALL decisions automatically!")
st.sidebar.markdown("---")

# API Key input
# Pre-filled from .env if available
# Hidden with dots for security
openai_key = st.sidebar.text_input(
    "🔑 OpenAI API Key",
    value=os.getenv("OPENAI_API_KEY", ""),
    type="password")

if openai_key:

    # ─────────────────────────────
    # Initialize once per session
    # session_state persists between
    # page reruns (button clicks etc)
    # Without this everything resets!
    # ─────────────────────────────
    if "rag_tool" not in st.session_state:
        # Create RAG tool
        st.session_state.rag_tool = (
            RAGTool(openai_key))

        # Create MCP Agent with RAG tool
        # MCP needs RAG to search documents
        st.session_state.mcp_agent = (
            MCPAgent(
                openai_key,
                st.session_state.rag_tool))

        # Empty chat history
        st.session_state.messages = []

    st.sidebar.markdown("---")

    # ─────────────────────────────
    # PDF Upload
    # Optional - MCP searches if uploaded
    # Can upload multiple files!
    # ─────────────────────────────
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
            # Unique key prevents reloading
            # Same file twice!
            key = f"loaded_{f.name}"

            if key not in st.session_state:
                with st.spinner(
                        f"📚 Indexing {f.name}"):
                    success, info = (
                        st.session_state
                        .rag_tool.load_pdf(f))

                    if success:
                        st.session_state[key] = True
                        st.sidebar.success(
                            f"✅ {f.name} "
                            f"({info} chunks)")
                    else:
                        st.sidebar.error(
                            f"❌ {info}")

    st.sidebar.markdown("---")

    # ─────────────────────────────
    # Tool Status Display
    # Show what MCP has available
    # ─────────────────────────────
    st.sidebar.subheader("🤖 MCP Tools Ready")

    tools_list = [
        "🌐 Web Search",
        "📖 Wikipedia",
        "📰 News Search",
        "📊 Report Generator",
        "💾 Report Saver",
        "🕐 Date & Time"
    ]

    # Check document status
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


# ===========================================
# MAIN INTERFACE
# ===========================================
st.title("🔬 MCP Research Assistant")
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

    # ─────────────────────────────
    # Demo Question Buttons
    # ─────────────────────────────
    st.subheader("💡 Try These Demo Questions")
    col1, col2, col3 = st.columns(3)

    # Button 1: Simple research
    q1 = col1.button(
        "🌍 Research AI developments",
        use_container_width=True)

    # Button 2: With documents
    q2 = col2.button(
        "🚀 Research Mars + my documents",
        use_container_width=True)

    # Button 3: Full report
    q3 = col3.button(
        "📊 Quantum computing full report",
        use_container_width=True)

    st.markdown("---")

    # ─────────────────────────────
    # CHAT HISTORY DISPLAY
    # Show all previous messages
    # with badges and steps
    # ─────────────────────────────

    # Color for each tool
    # Very visual for demo!
    TOOL_COLORS = {
        "web_search": "#4CAF50",       # Green
        "wikipedia_search": "#2196F3",  # Blue
        "news_search": "#FF9800",       # Orange
        "search_documents": "#9C27B0",  # Purple
        "generate_report": "#F44336",   # Red
        "save_report": "#795548",       # Brown
        "get_current_datetime": "#607D8B" # Grey
    }

    for msg in st.session_state.get(
            "messages", []):

        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])

        else:
            with st.chat_message(
                    "assistant",
                    avatar="🔬"):

                # Show tool badges
                if msg.get("tools_used"):
                    st.markdown(
                        "**🤖 MCP Used:**")
                    badges = ""
                    for tool in (
                            msg["tools_used"]):
                        color = TOOL_COLORS.get(
                            tool, "#999")
                        badges += (
                            f'<span class="tool-badge" '
                            f'style="background:{color};'
                            f'color:white">'
                            f'{tool}</span> ')
                    st.markdown(
                        badges,
                        unsafe_allow_html=True)

                # Show research steps
                # Click to expand!
                if msg.get("steps"):
                    with st.expander(
                            f"🔍 MCP Research Steps "
                            f"({len(msg['steps'])})"):
                        for step in msg["steps"]:
                            st.markdown(
                                f'<div class="step-box">'
                                f'{step}</div>',
                                unsafe_allow_html=True)

                # Final answer
                st.write(msg["content"])

    # ─────────────────────────────
    # CHAT INPUT
    # Bottom of screen like chat apps
    # ─────────────────────────────
    user_input = st.chat_input(
        "Ask me to research anything — "
        "MCP decides how to find it!")

    # Handle demo button clicks
    # Set predefined questions
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

    # ─────────────────────────────
    # PROCESS USER INPUT
    # ─────────────────────────────
    if user_input:

        # Show user message immediately
        with st.chat_message("user"):
            st.write(user_input)

        # Save to history
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        # MCP Agent does all the work!
        with st.chat_message(
                "assistant",
                avatar="🔬"):

            with st.spinner(
                    "🤖 MCP researching — "
                    "deciding tools to use..."):
                # Just pass question to MCP!
                # MCP handles EVERYTHING else!
                result = (
                    st.session_state
                    .mcp_agent.research(
                        user_input))

            # Show tool badges
            if result["tools_used"]:
                st.markdown(
                    "**🤖 MCP Automatically Used:**")
                badges = ""
                for tool in result["tools_used"]:
                    color = TOOL_COLORS.get(
                        tool, "#999")
                    badges += (
                        f'<span class="tool-badge" '
                        f'style="background:{color};'
                        f'color:white">'
                        f'{tool}</span> ')
                st.markdown(
                    badges,
                    unsafe_allow_html=True)

            # Show research steps
            if result["steps"]:
                with st.expander(
                        f"🔍 MCP Research Steps "
                        f"({len(result['steps'])})"):
                    for step in result["steps"]:
                        st.markdown(
                            f'<div class="step-box">'
                            f'{step}</div>',
                            unsafe_allow_html=True)

            # Show final answer
            st.write(result["answer"])

        # Save to history with metadata
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "tools_used": result["tools_used"],
            "steps": result["steps"]
        })

else:
    # No API key yet - guide user
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