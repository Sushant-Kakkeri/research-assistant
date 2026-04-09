# ===========================================
# mcp_agent.py
# ===========================================
# THE BRAIN of the entire application!
#
# This is where MCP lives and thinks.
# MCP makes ALL decisions - no router!
#
# HOW THE MCP AGENT LOOP WORKS:
#
# Previous app (with router):
# User → App → Router → RAG or MCP → Answer
# One decision. One step.
#
# This app (MCP Agent):
# User → App → MCP starts thinking...
#            → MCP calls web_search
#            → MCP reads result
#            → MCP calls wikipedia
#            → MCP reads result
#            → MCP calls search_documents
#            → MCP reads result
#            → MCP has enough info!
#            → MCP writes final answer
#
# Multiple iterations! Keeps going
# until it has enough information!
# THAT is what makes it an AGENT!
# ===========================================

# OpenAI - powers MCP's thinking
from openai import OpenAI

# Tools and executor from tools.py
from tools import ALL_TOOLS, execute_tool

# Parse JSON tool arguments from OpenAI
# OpenAI returns args as JSON string
# Convert to Python dict to use them
import json


# ===========================================
# MCP SYSTEM PROMPT
# ===========================================
# The instruction manual for MCP.
# Like an employee handbook!
# CRITICAL: Better prompt = smarter MCP!
# ===========================================
MCP_SYSTEM_PROMPT = """You are an advanced
AI Research Assistant powered by MCP
(Model Context Protocol).

YOUR ROLE:
YOU are the intelligent decision maker.
No router tells you what to do.
YOU decide which tools to use,
in what order, and how many times.

YOUR AVAILABLE TOOLS:
1. web_search - Current internet information
2. wikipedia_search - Deep background knowledge
3. news_search - Latest news this week
4. search_documents - Search uploaded PDFs
   (RAG - your local documents NOT internet!)
5. generate_report - Compile into report
6. save_report - Save report to file
7. get_current_datetime - Current time

YOUR RESEARCH STRATEGY:
STEP 1 - UNDERSTAND
What is being asked?
What sources would help most?

STEP 2 - GATHER (use multiple tools!)
Always use at least 2-3 tools:
- search_documents: if PDFs uploaded
- wikipedia_search: for background
- web_search: for current facts
- news_search: for latest news

STEP 3 - COMPILE
Combine all findings.
Cite which tool found what.

STEP 4 - REPORT
Use generate_report for complex research.
Use save_report if user wants to save.

IMPORTANT RULES:
✅ Always use 2+ tools for any research
✅ Always cite sources in your answer
✅ Use search_documents if docs available
✅ Generate report for complex questions
✅ Be thorough - check multiple sources

REMEMBER: You are an AGENT not a chatbot.
Agents TAKE ACTIONS (use tools).
Chatbots just answer from memory.
USE YOUR TOOLS!"""


# ===========================================
# MCPAgent CLASS
# ===========================================
class MCPAgent:
    """
    The MCP Agent - the intelligent brain.
    Makes all decisions. No router needed!
    """

    def __init__(self,
                 openai_key: str,
                 rag_tool=None):
        """
        Initialize MCP Agent.

        Args:
            openai_key: OpenAI API key
            rag_tool:   RAG tool instance
                        MCP calls this to
                        search documents
        """
        # OpenAI connection = MCP's brain
        self.client = OpenAI(
            api_key=openai_key)

        # RAG tool for document search
        # MCP calls this like any other tool
        self.rag_tool = rag_tool

        # Conversation memory
        # Stores past Q&A for context
        # Like short term memory!
        self.conversation_history = []

        # Tool usage tracking
        self.tool_calls_made = []

    def research(self,
                 query: str) -> dict:
        """
        Main research method.
        MCP handles EVERYTHING here!

        Args:
            query: User's question

        Returns:
            Dict with:
            - answer: Final response
            - tools_used: Tool names list
            - tool_results: Results dict
            - steps: Research steps list
        """

        # Initialize return dictionary
        result = {
            "answer": "",
            "tools_used": [],
            "tool_results": {},
            "steps": []
        }

        # ─────────────────────────────
        # BUILD MESSAGES
        # Start with system instructions
        # Add conversation history
        # Add current question
        # ─────────────────────────────

        # System prompt goes first
        messages = [{
            "role": "system",
            "content": MCP_SYSTEM_PROMPT
        }]

        # Add last 6 messages from history
        # (3 Q&A exchanges = enough context)
        for msg in (
                self.conversation_history[-6:]):
            messages.append(msg)

        # ─────────────────────────────
        # TELL MCP ABOUT DOCUMENTS
        # MCP needs to know what PDFs
        # are available to search!
        # ─────────────────────────────
        has_docs = (
            self.rag_tool and
            self.rag_tool.has_documents())

        doc_status = ""
        if has_docs:
            files = (
                self.rag_tool.get_loaded_files())
            # Tell MCP what files exist
            # This triggers it to use
            # search_documents tool!
            doc_status = (
                f"\n\n📄 DOCUMENTS AVAILABLE:\n"
                f"These PDFs can be searched:\n"
                f"{chr(10).join(f'• {f}' for f in files)}\n"
                f"Use search_documents tool!")

        # Add question + doc info
        messages.append({
            "role": "user",
            "content": f"{query}{doc_status}"
        })

        # ===========================================
        # THE MCP AGENT LOOP
        # ===========================================
        # This is the CORE of the agent!
        #
        # Each iteration:
        # 1. Ask OpenAI what to do next
        # 2. If it wants a tool → run it
        #    → add result to messages
        #    → loop again!
        # 3. If it's done → get answer
        #    → stop looping
        #
        # MCP keeps looping until it has
        # enough information to answer!
        # ===========================================

        max_iterations = 10  # Safety limit!
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Ask OpenAI what to do
            # Pass all messages + tool menu
            response = self.client.chat\
                .completions.create(
                    model="gpt-4o",    # Best model
                    messages=messages, # Full history
                    tools=ALL_TOOLS,   # Tool menu
                    # auto = MCP decides when to use tools
                    tool_choice="auto",
                    temperature=0.3    # Consistent decisions
                )

            response_message = (
                response.choices[0].message)

            # ─────────────────────────────
            # Did MCP request any tools?
            # ─────────────────────────────
            if response_message.tool_calls:
                # YES! MCP wants to use tools!

                # Add MCP's decision to history
                messages.append(response_message)

                # Execute each tool requested
                # (MCP can request multiple at once!)
                for tool_call in (
                        response_message.tool_calls):

                    # Get tool name
                    # Example: "web_search"
                    tool_name = (
                        tool_call.function.name)

                    # Get arguments
                    # OpenAI gives us JSON string
                    # json.loads converts to dict
                    tool_args = json.loads(
                        tool_call.function.arguments)

                    # Track step for display
                    # Shows audience MCP thinking!
                    first_arg = (
                        list(tool_args.values())[0]
                        if tool_args else "")

                    step_text = (
                        f"🔧 MCP chose: {tool_name}"
                        f"({first_arg[:50]}...)"
                        if len(str(first_arg)) > 50
                        else
                        f"🔧 MCP chose: {tool_name}"
                        f"({first_arg})")
                    result["steps"].append(step_text)

                    # RUN THE TOOL!
                    tool_result = execute_tool(
                        tool_name,
                        tool_args,
                        self.rag_tool  # For doc search
                    )

                    # Track tools used
                    if tool_name not in (
                            result["tools_used"]):
                        result["tools_used"]\
                            .append(tool_name)
                    result["tool_results"][
                        tool_name] = tool_result

                    # Add result to messages
                    # THIS IS HOW MCP LEARNS!
                    # It reads what tool returned
                    # then decides if needs more info
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": tool_result
                    })

                # Loop continues!
                # MCP reads results and decides
                # next action automatically

            else:
                # NO tool calls!
                # MCP has enough info!
                # Get final answer and stop!
                result["answer"] = (
                    response_message.content)
                break  # Exit the loop!

        # If hit max without answer
        if not result["answer"]:
            result["answer"] = (
                "Research complete. "
                "Max tool calls reached.")

        # Save to conversation history
        # For context in future questions
        self.conversation_history.append({
            "role": "user",
            "content": query
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": result["answer"]
        })

        return result

    def clear_history(self):
        """Clear conversation memory."""
        self.conversation_history = []
        self.tool_calls_made = []