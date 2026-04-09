# ===========================================
# tools.py
# ===========================================
# This file is the TOOLBOX.
# All tools MCP can use live here.
# MCP picks tools from here like a
# worker picking tools from a hardware store!
#
# Tools available:
# 1. web_search       - Search internet
# 2. wikipedia_search - Background knowledge
# 3. news_search      - Latest news
# 4. generate_report  - Create report
# 5. save_report      - Save to file
# 6. get_current_datetime - Current time
# ===========================================

# datetime = Python built in date/time
from datetime import datetime

# requests = lets Python talk to websites
# Like Python's own web browser
import requests

# os = interact with computer files/folders
import os


# ===========================================
# TOOL 1: WEB SEARCH
# ===========================================
# Searches the internet for live information.
# MCP calls this when it needs current data.
#
# Has 3 fallback attempts:
# 1. DuckDuckGo with time limit (best)
# 2. DuckDuckGo without time limit (backup)
# 3. Wikipedia (last resort)
# ===========================================
def web_search(query: str) -> str:
    """
    Search the web for current information.

    Args:
        query: What to search for
               Example: "Mars missions 2026"
    Returns:
        String with search results
    """

    # ─────────────────────────────
    # ATTEMPT 1: DuckDuckGo with time limit
    # timelimit='m' = last month only
    # Most current results!
    # ─────────────────────────────
    try:
        from duckduckgo_search import DDGS

        # 'with' = auto close connection
        # Like opening/closing a door properly
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query,            # Search term
                max_results=5,    # Get 5 results
                region='us-en',   # US English
                safesearch='off', # All results
                timelimit='m'     # Last month
            ))

        # Format results if we got any
        if results:
            formatted = []
            for r in results:
                formatted.append(
                    f"**{r['title']}**\n"
                    f"{r['body']}\n"
                    f"Source: {r['href']}")
            return "\n\n".join(formatted)

    except Exception:
        pass  # Try next approach

    # ─────────────────────────────
    # ATTEMPT 2: DuckDuckGo no time limit
    # Broader search as backup
    # ─────────────────────────────
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query,
                max_results=5,
                region='us-en'
                # No timelimit!
            ))

        if results:
            formatted = []
            for r in results:
                formatted.append(
                    f"**{r['title']}**\n"
                    f"{r['body']}\n"
                    f"Source: {r['href']}")
            return "\n\n".join(formatted)

    except Exception:
        pass  # Try next approach

    # ─────────────────────────────
    # ATTEMPT 3: Wikipedia fallback
    # If web search completely fails
    # use Wikipedia as backup source
    # ─────────────────────────────
    try:
        import wikipedia
        wikipedia.set_lang("en")
        search_results = wikipedia.search(
            query, results=3)

        if search_results:
            for result in search_results:
                try:
                    summary = wikipedia.summary(
                        result,
                        sentences=5,
                        auto_suggest=False)
                    page = wikipedia.page(
                        result,
                        auto_suggest=False)
                    return (
                        f"📖 From Wikipedia "
                        f"(web search "
                        f"unavailable):\n\n"
                        f"**{page.title}**\n\n"
                        f"{summary}\n\n"
                        f"Source: {page.url}")
                except Exception:
                    continue

    except Exception:
        pass

    # Last resort - helpful message
    return (
        f"🔍 Web search temporarily "
        f"unavailable for '{query}'.\n"
        f"Please try a more specific term.")


# ===========================================
# TOOL 2: WIKIPEDIA SEARCH
# ===========================================
# Gets deep background knowledge
# from Wikipedia on any topic.
#
# Uses exact match first then broader search.
# Handles disambiguation (Mercury = planet
# OR element OR car brand).
# Tries multiple results until one works.
# ===========================================
def wikipedia_search(topic: str) -> str:
    """
    Search Wikipedia for background knowledge.

    Args:
        topic: Topic to research
               Example: "International Space Station"
    Returns:
        Wikipedia article summary with URL
    """
    try:
        import wikipedia
        wikipedia.set_lang("en")

        # STEP 1: Exact match search
        # Quotes = find exact phrase
        # "SpaceX" finds SpaceX company
        # not just anything with "space"
        search_results = wikipedia.search(
            f'"{topic}"', results=5)

        # STEP 2: Broader search if needed
        if not search_results:
            search_results = wikipedia.search(
                topic, results=5)

        if not search_results:
            return (
                f"No Wikipedia results "
                f"found for '{topic}'.")

        # STEP 3: Try each result
        # Some pages have errors so
        # try next one if current fails
        for result in search_results:
            try:
                # Get 8 sentence summary
                summary = wikipedia.summary(
                    result,
                    sentences=8,
                    auto_suggest=False)
                page = wikipedia.page(
                    result,
                    auto_suggest=False)
                return (
                    f"📖 Wikipedia: "
                    f"**{page.title}**\n\n"
                    f"{summary}\n\n"
                    f"Source: {page.url}")

            # Handle disambiguation
            # Example: "Mercury" could be
            # planet, element, or car!
            except wikipedia\
                    .DisambiguationError as e:
                try:
                    # Use first/most likely option
                    summary = wikipedia.summary(
                        e.options[0],
                        sentences=8,
                        auto_suggest=False)
                    page = wikipedia.page(
                        e.options[0],
                        auto_suggest=False)
                    return (
                        f"📖 Wikipedia: "
                        f"**{page.title}**\n\n"
                        f"{summary}\n\n"
                        f"Source: {page.url}\n\n"
                        f"💡 Related: "
                        f"{', '.join(e.options[1:4])}")
                except Exception:
                    continue

            except Exception:
                continue  # Try next result

        return (
            f"⚠️ Could not load Wikipedia "
            f"for '{topic}'.")

    except Exception as e:
        return f"Wikipedia error: {str(e)}"


# ===========================================
# TOOL 3: NEWS SEARCH
# ===========================================
# Finds the VERY LATEST news articles.
# Different from web_search:
# - Uses DuckDuckGo NEWS specifically
# - Only last week's articles
# - Returns article titles and dates
# ===========================================
def news_search(topic: str) -> str:
    """
    Search for latest news on any topic.

    Args:
        topic: What news to find
               Example: "SpaceX launches"
    Returns:
        5 most recent news articles
    """
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            # .news() = news only search
            # different from .text()!
            results = list(ddgs.news(
                topic,
                max_results=5,
                region='us-en',
                safesearch='off',
                timelimit='w'  # Last WEEK only!
                # 'd'=day 'w'=week 'm'=month
            ))

        if results:
            # Build formatted news list
            formatted = [
                f"📰 Latest News: {topic}\n"]
            for r in results:
                date = r.get('date', 'Recent')
                formatted.append(
                    f"**{r['title']}**\n"
                    f"Date: {date}\n"
                    f"{r['body']}\n"
                    f"Source: {r['url']}")
            return "\n\n".join(formatted)

    except Exception:
        pass

    # Fallback to web search with year
    return web_search(
        f"latest news {topic} 2026")


# ===========================================
# TOOL 4: GET CURRENT DATETIME
# ===========================================
# Returns current date and time.
# Used by MCP to timestamp reports.
# ===========================================
def get_current_datetime() -> str:
    """Get current date and time."""
    now = datetime.now()
    return (
        f"📅 Current Date & Time:\n"
        f"Date: "
        f"{now.strftime('%A, %B %d, %Y')}\n"
        f"Time: {now.strftime('%I:%M %p')}")


# ===========================================
# TOOL 5: GENERATE REPORT
# ===========================================
# Takes all research MCP gathered and
# formats it into a professional report.
# MCP calls this AFTER gathering all info.
# ===========================================
def generate_report(
        topic: str,   # Report subject
        content: str  # All research content
) -> str:
    """
    Generate structured research report.

    Args:
        topic:   Research subject
        content: All gathered research
    Returns:
        Professionally formatted report
    """
    now = datetime.now()
    report = (
        f"{'=' * 50}\n"
        f"RESEARCH REPORT\n"
        f"{'=' * 50}\n"
        f"Topic: {topic}\n"
        f"Generated: "
        f"{now.strftime('%B %d, %Y %I:%M %p')}\n"
        f"{'=' * 50}\n\n"
        f"{content}\n\n"  # All research here!
        f"{'=' * 50}\n"
        f"END OF REPORT\n"
        f"{'=' * 50}")
    return report


# ===========================================
# TOOL 6: SAVE REPORT
# ===========================================
# Saves generated report to a real file!
# Creates: reports/Mars_20260406_223015.txt
#
# Steps:
# 1. Create reports folder
# 2. Clean topic for filename
# 3. Add timestamp (unique filename)
# 4. Write to file
# ===========================================
def save_report(
        topic: str,   # Used for filename
        content: str  # What to save
) -> str:
    """
    Save research report to a file.

    Args:
        topic:   Topic name for filename
        content: Complete report content
    Returns:
        Success message with filename
    """
    try:
        # Create reports folder if not exists
        # exist_ok=True = no error if exists
        os.makedirs("reports", exist_ok=True)

        # Clean topic for filename
        # Remove special characters Windows
        # doesn't allow in filenames!
        clean_topic = "".join(
            c if c.isalnum() or c in (' ', '-')
            else '_'
            for c in topic)

        # Max 30 chars, underscores not spaces
        clean_topic = clean_topic[:30]\
            .strip().replace(' ', '_')

        # Add timestamp to filename
        # Prevents overwriting old reports!
        # Mars_20260406_223015.txt
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d_%H%M%S')

        filename = (
            f"reports/"
            f"{clean_topic}_"
            f"{timestamp}.txt")

        # Write report to file
        # 'w' = write mode
        # encoding='utf-8' handles special chars
        with open(filename, 'w',
                  encoding='utf-8') as f:
            f.write(content)

        return (
            f"✅ Report saved!\n"
            f"📁 File: {filename}\n"
            f"📊 Size: {len(content)} chars\n"
            f"🕐 At: "
            f"{now.strftime('%I:%M %p')}")

    except Exception as e:
        return f"❌ Could not save: {str(e)}"


# ===========================================
# ALL TOOL DEFINITIONS FOR MCP
# ===========================================
# This is the MENU we give to GPT-4o.
# GPT reads descriptions and decides
# which tool to call and when!
#
# Like a restaurant menu:
# - Each tool is a dish
# - Description = when to order it
# - Parameters = what info to provide
#
# CRITICAL: Better descriptions =
#           Smarter MCP decisions!
# ===========================================
ALL_TOOLS = [

    # ─────────────────────────────
    # Tool 1: web_search
    # Use for: current/live information
    # ─────────────────────────────
    {
        "type": "function",
        "function": {
            # Must exactly match function name!
            "name": "web_search",
            # This tells GPT WHEN to use it
            "description":
                "Search the web for current "
                "live information and data. "
                "Use for latest developments, "
                "current facts, recent events "
                "and anything needing up-to-date "
                "information from the internet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description":
                            "Specific search query. "
                            "Be precise for results. "
                            "Example: "
                            "'NASA Mars rover 2026'"
                    }
                },
                "required": ["query"]
            }
        }
    },

    # ─────────────────────────────
    # Tool 2: wikipedia_search
    # Use for: background/definitions
    # ─────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "wikipedia_search",
            "description":
                "Search Wikipedia for "
                "background knowledge, "
                "history, definitions and "
                "general information. "
                "Use for deep understanding "
                "of any subject or topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description":
                            "Full official topic name. "
                            "Example: "
                            "'International Space Station'"
                    }
                },
                "required": ["topic"]
            }
        }
    },

    # ─────────────────────────────
    # Tool 3: news_search
    # Use for: breaking news this week
    # ─────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "news_search",
            "description":
                "Search for the very latest "
                "news articles from this week. "
                "Use specifically for recent "
                "news, current events and "
                "breaking developments. "
                "More current than web_search!",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description":
                            "Topic for news search. "
                            "Example: 'SpaceX Starship'"
                    }
                },
                "required": ["topic"]
            }
        }
    },

    # ─────────────────────────────
    # Tool 4: search_documents
    # THIS IS RAG AS AN MCP TOOL!
    # Use for: uploaded PDF documents
    # ─────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            # Tell GPT this is LOCAL files
            # not internet!
            "description":
                "Search through uploaded PDF "
                "documents and local files. "
                "Use when user mentions documents, "
                "PDFs, uploaded files or stored "
                "knowledge. Searches YOUR files "
                "not the internet. "
                "This is RAG search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description":
                            "What to search for "
                            "in uploaded documents. "
                            "Example: 'Mars temperature'"
                    }
                },
                "required": ["query"]
            }
        }
    },

    # ─────────────────────────────
    # Tool 5: generate_report
    # Use for: compiling research
    # ─────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "generate_report",
            "description":
                "Generate a structured "
                "professional research report. "
                "Use AFTER collecting enough "
                "research from other tools. "
                "Creates formatted document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description":
                            "Main research topic."
                    },
                    "content": {
                        "type": "string",
                        "description":
                            "All research content "
                            "to include in report."
                    }
                },
                "required": ["topic", "content"]
            }
        }
    },

    # ─────────────────────────────
    # Tool 6: save_report
    # Use for: saving report to file
    # ─────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "save_report",
            "description":
                "Save research report to "
                "a file on the computer. "
                "Use AFTER generating report "
                "to save it permanently.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description":
                            "Topic for filename."
                    },
                    "content": {
                        "type": "string",
                        "description":
                            "Complete report to save."
                    }
                },
                "required": ["topic", "content"]
            }
        }
    },

    # ─────────────────────────────
    # Tool 7: get_current_datetime
    # Use for: timestamps
    # ─────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description":
                "Get current date and time. "
                "Use for timestamps and when "
                "user asks current time.",
            "parameters": {
                "type": "object",
                # No parameters needed!
                "properties": {},
                "required": []
            }
        }
    }
]


# ===========================================
# EXECUTE TOOL FUNCTION
# ===========================================
# The DISPATCHER — runs tools when MCP calls.
#
# Like a phone operator:
# MCP dials a number (tool name)
# Operator connects call (runs function)
# Result goes back to MCP
#
# Special case for RAG:
# RAG needs its own engine so handled
# separately from other tools!
# ===========================================
def execute_tool(
        tool_name: str,   # Which tool to run
        tool_args: dict,  # Arguments to pass
        rag_engine=None   # RAG tool instance
) -> str:
    """
    Execute any tool by name.

    Args:
        tool_name:  Name of tool to run
        tool_args:  Dict of arguments
        rag_engine: RAG instance if available

    Returns:
        Tool result as string
    """

    # ─────────────────────────────
    # Special handling for RAG search
    # RAG needs its own engine
    # Can't just be in tools dict
    # ─────────────────────────────
    if tool_name == "search_documents":
        if rag_engine and (
                rag_engine.has_documents()):
            result = rag_engine.search(
                tool_args.get("query", ""))
            if result:
                return (
                    f"📄 From Documents:\n\n"
                    f"{result}")
            return (
                "No relevant content found "
                "in uploaded documents.")
        return (
            "⚠️ No documents uploaded yet. "
            "Please upload a PDF first.")

    # ─────────────────────────────
    # All other tools in dictionary
    # Maps name (string) → function
    # ─────────────────────────────
    tools = {
        "web_search": web_search,
        "wikipedia_search": wikipedia_search,
        "news_search": news_search,
        "get_current_datetime":
            get_current_datetime,
        "generate_report": generate_report,
        "save_report": save_report
    }

    if tool_name in tools:
        try:
            # **tool_args unpacks the dict
            # Like: web_search(query="Mars")
            return tools[tool_name](**tool_args)
        except Exception as e:
            return (
                f"⚠️ Tool error: {str(e)}")

    return f"❌ Unknown tool: {tool_name}"