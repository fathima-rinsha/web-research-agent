import json
import re
import os
import google.generativeai as genai

# Load Google Gemini API key from environment
gemini_api_key = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

SYSTEM_PROMPT = """You are an expert research analyst.

When given a research topic, provide a comprehensive intelligence briefing.

RESPONSE FORMAT: You MUST respond with ONLY a valid JSON object. Do not include any text before or after the JSON.

Use this exact JSON structure:
{
  "executive_summary": "A concise 2-3 sentence overview of the topic.",
  "key_findings": [
    {"title": "Finding 1 Title", "detail": "Detailed explanation of finding 1"},
    {"title": "Finding 2 Title", "detail": "Detailed explanation of finding 2"}
  ],
  "analysis": "A comprehensive paragraph analyzing the key findings and their implications.",
  "conclusion": "A brief forward-looking conclusion or takeaway.",
  "sources": [
    {"title": "Source 1 Name", "url": "https://example.com/article1"},
    {"title": "Source 2 Name", "url": "https://example.com/article2"}
  ]
}

Requirements:
- Include 5-8 key findings
- Include 4-6 sources with real URLs
- All fields must be strings or arrays, never null
- Response MUST be valid, parseable JSON
- Do NOT include markdown code blocks or extra text
"""


def parse_response(text: str, search_queries: list) -> dict:
    """Parse Gemini's JSON response into a structured dict."""
    if not text or not text.strip():
        return {
            "executive_summary": "No response received.",
            "key_findings": [],
            "analysis": "",
            "conclusion": "",
            "sources": [],
            "search_queries": search_queries,
            "error": "Empty response from Gemini",
        }

    clean = text.strip()

    # Strip markdown code fences if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", clean)
    if match:
        clean = match.group(1).strip()

    # Remove any trailing/leading whitespace and try to find JSON object boundaries
    json_match = re.search(r"\{[\s\S]*\}", clean)
    if json_match:
        clean = json_match.group(0)

    try:
        result = json.loads(clean)
        
        # Validate response structure
        if not isinstance(result, dict):
            raise ValueError("Response is not a JSON object")
        
        # Ensure all required fields exist
        required = ["executive_summary", "key_findings", "analysis", "conclusion", "sources"]
        for field in required:
            if field not in result:
                result[field] = "" if field != "key_findings" and field != "sources" else []
        
        result["search_queries"] = search_queries
        return result
        
    except json.JSONDecodeError as e:
        return {
            "executive_summary": clean[:500] if clean else "Research completed but response parsing failed.",
            "key_findings": [],
            "analysis": clean[500:] if len(clean) > 500 else "",
            "conclusion": "",
            "sources": [],
            "search_queries": search_queries,
            "parse_error": True,
            "error": f"JSON parsing failed: {str(e)}",
        }
    except Exception as e:
        return {
            "executive_summary": "An error occurred while parsing the response.",
            "key_findings": [],
            "analysis": str(e),
            "conclusion": "",
            "sources": [],
            "search_queries": search_queries,
            "error": f"Parse error: {str(e)}",
        }


def run_research(topic: str) -> dict:
    """
    Run research using Google Gemini API (generous free tier).
    """
    search_queries = []

    # Check if API key exists
    if not gemini_api_key:
        return {
            "executive_summary": "API Error: GOOGLE_API_KEY not found in environment variables",
            "key_findings": [],
            "analysis": "Make sure GOOGLE_API_KEY is set in your .env file or Render environment settings",
            "conclusion": "",
            "sources": [],
            "search_queries": search_queries,
            "error": "GOOGLE_API_KEY not configured",
        }

    try:
        # Use Gemini 1.5 Flash (free tier, very fast)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"{SYSTEM_PROMPT}\n\nResearch this topic thoroughly and provide a comprehensive briefing: {topic}"
        
        response = model.generate_content(prompt)
        
        text_content = response.text
        return parse_response(text_content, search_queries)

    except Exception as e:
        error_msg = str(e)
        return {
            "executive_summary": f"API Error: {error_msg}",
            "key_findings": [],
            "analysis": "Check that your Google API key is valid and has Gemini API enabled.",
            "conclusion": "",
            "sources": [],
            "search_queries": search_queries,
            "error": f"Gemini API call failed: {error_msg}",
        }