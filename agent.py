import anthropic
import json
import re

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are an expert research analyst with access to real-time web search.

When given a research topic:
1. Perform multiple targeted web searches to gather comprehensive, current information
2. Cross-reference findings from multiple sources
3. Synthesize into a professional intelligence briefing

CRITICAL: Respond ONLY with a valid JSON object — no markdown, no code blocks, no preamble. Use this exact structure:

{
  "executive_summary": "2-3 sentence high-level overview of the topic",
  "key_findings": [
    {"title": "Short finding title", "detail": "Detailed explanation of this finding (2-3 sentences)"}
  ],
  "analysis": "A deeper analytical paragraph connecting the findings, identifying patterns, implications, or contradictions across sources",
  "conclusion": "A brief forward-looking conclusion or key takeaway",
  "sources": [
    {"title": "Source title or publication name", "url": "https://full-url-here"}
  ]
}

Aim for 5-8 key findings and at least 4-6 sources. Be thorough and objective.
"""


def parse_response(text: str, search_queries: list) -> dict:
    """Parse Claude's JSON response into a structured dict."""
    clean = text.strip()

    # Strip markdown code fences if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", clean)
    if match:
        clean = match.group(1).strip()

    try:
        result = json.loads(clean)
        result["search_queries"] = search_queries
        return result
    except json.JSONDecodeError:
        # Fallback: return raw text in a safe structure
        return {
            "executive_summary": clean[:400] if clean else "Research completed.",
            "key_findings": [],
            "analysis": clean,
            "conclusion": "",
            "sources": [],
            "search_queries": search_queries,
            "parse_error": True,
        }


def run_research(topic: str) -> dict:
    """
    Run the research agent on a given topic.
    Uses Claude with the built-in web_search tool for real-time information.
    Handles both single-turn and multi-turn (agentic loop) responses.
    """
    messages = [
        {
            "role": "user",
            "content": f"Research this topic thoroughly and produce a comprehensive intelligence briefing: {topic}",
        }
    ]

    search_queries = []
    max_iterations = 8  # Safety cap on the agentic loop

    for iteration in range(max_iterations):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=messages,
        )

        # Separate text and tool_use blocks
        text_content = ""
        tool_uses = []

        for block in response.content:
            block_type = getattr(block, "type", None)
            if block_type == "text":
                text_content += block.text
            elif block_type == "tool_use":
                tool_uses.append(block)
                if block.name == "web_search":
                    query = getattr(block, "input", {}).get("query", "")
                    if query:
                        search_queries.append(query)

        # If no more tool calls pending, we have the final response
        if not tool_uses or response.stop_reason == "end_turn":
            return parse_response(text_content, search_queries)

        # Continue agentic loop: append assistant turn + tool results
        messages.append({"role": "assistant", "content": response.content})

        tool_results = [
            {
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": "Search executed successfully.",
            }
            for block in tool_uses
        ]
        messages.append({"role": "user", "content": tool_results})

    # Fallback if we hit the iteration cap
    return {
        "executive_summary": "Research exceeded maximum iterations.",
        "key_findings": [],
        "analysis": "",
        "conclusion": "",
        "sources": [],
        "search_queries": search_queries,
        "error": "Max agent iterations reached",
    }
