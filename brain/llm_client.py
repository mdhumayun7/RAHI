"""
RAHI LLM Client — Provider-Agnostic Abstraction Layer
Supports: GitHub Models | Groq | Gemini | Anthropic | OpenAI
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_llm_response(prompt: str, system: str = "You are RAHI, a helpful AI assistant.") -> str:
    github_token  = os.getenv("GITHUB_TOKEN")
    groq_key      = os.getenv("GROQ_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key    = os.getenv("OPENAI_API_KEY")

    if github_token:
        return _call_github(prompt, system, github_token)
    elif groq_key:
        return _call_groq(prompt, system, groq_key)
    elif anthropic_key:
        return _call_anthropic(prompt, system, anthropic_key)
    elif openai_key:
        return _call_openai(prompt, system, openai_key)
    else:
        raise ValueError("No API key found in .env file!")


def _call_github(prompt: str, system: str, token: str) -> str:
    """Call GitHub Models — Free with GitHub account."""
    from openai import OpenAI

    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=token,
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt},
        ],
        max_tokens=500,
        temperature=0.7,
    )
    return response.choices[0].message.content


def _call_groq(prompt: str, system: str, api_key: str) -> str:
    """Call Groq — Free, Llama-3 based."""
    from groq import Groq

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt},
        ],
        max_tokens=500,
        temperature=0.7,
    )
    return response.choices[0].message.content


def _call_anthropic(prompt: str, system: str, api_key: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def _call_openai(prompt: str, system: str, api_key: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt},
        ],
        max_tokens=500,
    )
    return response.choices[0].message.content


# ─── Quick test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🤖 Testing RAHI LLM Client...\n")

    response = get_llm_response(
        prompt="Say exactly this: 'RAHI is online. Phase 0 complete.'",
        system="You are RAHI. Follow instructions precisely."
    )

    print(f"RAHI says: {response}")
    print(f"📊 Response length: {len(response)} characters")
    print("\n✅ LLM Client is working!")