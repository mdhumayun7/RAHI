"""
RAHI Tool Registry
==================
Ye file define karti hai woh sab tools jo RAHI use kar sakta hai.

ReAct paper mein: Agent ko pata hona chahiye ki uske paas kya tools hain,
unka naam kya hai, aur kaise use kare.

Abhi hum 4 simple tools banate hain:
  1. calculator  - math calculations
  2. search      - web search simulate
  3. weather     - weather info
  4. finish      - task complete karo

Phase 3 mein ye real tools se replace honge (Playwright browser, etc.)
"""


def calculator(expression: str) -> str:
    """
    Safe math calculator.
    Input:  "2 + 2" or "15 * 4 / 2"
    Output: "4" or "30.0"
    """
    try:
        # Sirf math operations allow karo — eval se dangerous code na chale
        allowed = set("0123456789+-*/()., ")
        if not all(c in allowed for c in expression):
            return "Error: Invalid characters in expression"
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


def search(query: str) -> str:
    knowledge = {
        "capital of india":        "New Delhi is the capital of India.",
        "capital of france":       "Paris is the capital of France.",
        "iit bombay":              "IIT Bombay is located in Powai, Mumbai, Maharashtra.",
        "svnit":                   "SVNIT (Sardar Vallabhbhai National Institute of Technology) is located in Surat, Gujarat, India.",
        "python creator":          "Python was created by Guido van Rossum, first released in 1991.",
        "react paper":             "ReAct paper was published by Yao et al. in 2022 at Princeton and Google Brain.",
    }

    query_lower = query.lower().strip()
    for key, value in knowledge.items():
        if key in query_lower:          # exact substring match — pehle tha "any word" match
            return value

    return f"Search result for '{query}': No specific result found."


def weather(city: str) -> str:
    """
    Weather info simulator (Phase 5 mein real API se replace hoga).
    Input:  "Surat"
    Output: Weather description
    """
    weather_data = {
        "surat":   "Surat: 36°C, Humid, Partly cloudy. Typical summer weather in Gujarat.",
        "mumbai":  "Mumbai: 32°C, High humidity, Coastal breeze.",
        "delhi":   "Delhi: 40°C, Hot and dry, Clear skies.",
        "london":  "London: 15°C, Overcast, Light drizzle expected.",
        "new york": "New York: 22°C, Sunny, Pleasant weather.",
    }

    city_lower = city.lower().strip()
    return weather_data.get(city_lower, f"{city}: Weather data not available. Please check a weather service.")


def finish(answer: str) -> str:
    """
    Task completion tool — jab RAHI confident ho ki answer ready hai.
    Input:  Final answer string
    Output: Same string (signals the loop to stop)
    """
    return answer


# ─── Tool Registry ────────────────────────────────────────────────────────────
# Ye dictionary ReAct engine ko batati hai ki kaunse tools available hain
TOOLS = {
    "calculator": {
        "function":    calculator,
        "description": "Perform math calculations. Input: math expression like '2+2' or '15*4'",
        "example":     "calculator('25 * 4 + 10')",
    },
    "search": {
        "function":    search,
        "description": "Search for factual information. Input: search query string",
        "example":     "search('capital of India')",
    },
    "weather": {
        "function":    weather,
        "description": "Get weather information for a city. Input: city name",
        "example":     "weather('Surat')",
    },
    "finish": {
        "function":    finish,
        "description": "Use this when you have the final answer ready. Input: your final answer",
        "example":     "finish('The answer is 42')",
    },
}


def get_tools_description() -> str:
    """Returns a formatted string describing all available tools for the LLM prompt."""
    lines = []
    for name, info in TOOLS.items():
        lines.append(f"- {name}: {info['description']}")
        lines.append(f"  Example: {info['example']}")
    return "\n".join(lines)