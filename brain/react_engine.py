"""
RAHI ReAct Reasoning Engine
============================
Paper: "ReAct: Synergizing Reasoning and Acting in Language Models"
       Yao et al., 2022 — https://arxiv.org/abs/2210.03629

Core idea from the paper:
  Traditional LLMs either REASON (chain-of-thought) or ACT (tool use).
  ReAct combines both in an interleaved loop:

    Thought_1 → Action_1 → Observation_1
    Thought_2 → Action_2 → Observation_2
    ...
    Thought_n → Action: finish(answer)

This file implements that loop for RAHI.
"""

import re
from brain.llm_client import get_llm_response
from brain.tools import TOOLS, get_tools_description


# ─── Prompt Template ─────────────────────────────────────────────────────────

REACT_SYSTEM_PROMPT = """You are RAHI, an intelligent AI assistant that solves problems step by step.

You have access to these tools:
{tools}

STRICT FORMAT — you must follow this exactly:

Thought: [your reasoning about what to do next]
Action: tool_name('input')

OR when you have the final answer:

Thought: [your reasoning]
Action: finish('your complete final answer')

RULES:
1. Always start with Thought:
2. Always follow with Action: on the next line
3. Only ONE action per response
4. Wait for the Observation before continuing
5. Use finish() when you have the answer

Example:
Thought: I need to calculate 15% of 200.
Action: calculator('200 * 0.15')
"""

REACT_USER_TEMPLATE = """Goal: {goal}

{history}
Thought:"""


# ─── ReAct Engine ────────────────────────────────────────────────────────────

class ReActEngine:
    """
    The core reasoning engine for RAHI.

    Each call to .run(goal) starts a fresh ReAct loop:
      1. Build prompt with goal + history
      2. Call LLM → get Thought + Action
      3. Parse action → execute tool
      4. Add observation to history
      5. Repeat until finish() is called or max_steps reached
    """

    def __init__(self, max_steps: int = 6, verbose: bool = True):
        self.max_steps = max_steps
        self.verbose   = verbose

    def run(self, goal: str) -> str:
        """
        Run the ReAct loop for a given goal.
        Returns the final answer string.
        """
        history = ""
        final_answer = None

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"🎯 GOAL: {goal}")
            print(f"{'='*60}")

        for step in range(1, self.max_steps + 1):
            if self.verbose:
                print(f"\n--- Step {step} ---")

            # ── 1. Build prompt ──────────────────────────────────────────
            system = REACT_SYSTEM_PROMPT.format(tools=get_tools_description())
            user   = REACT_USER_TEMPLATE.format(goal=goal, history=history)

            # ── 2. Call LLM ──────────────────────────────────────────────
            raw_response = get_llm_response(prompt=user, system=system)

            # Add "Thought:" back since we stripped it from the prompt
            full_response = "Thought:" + raw_response

            if self.verbose:
                print(full_response)

            # ── 3. Parse Thought and Action ──────────────────────────────
            thought, tool_name, tool_input = self._parse_response(full_response)

            if not tool_name:
                if self.verbose:
                    print("⚠️  Could not parse action. Stopping.")
                break

            # ── 4. Execute Tool ──────────────────────────────────────────
            observation = self._execute_tool(tool_name, tool_input)

            if self.verbose:
                print(f"🔍 Observation: {observation}")

            # ── 5. Check if done ─────────────────────────────────────────
            if tool_name == "finish":
                final_answer = observation
                if self.verbose:
                    print(f"\n{'='*60}")
                    print(f"✅ FINAL ANSWER: {final_answer}")
                    print(f"{'='*60}")
                break

            # ── 6. Update history for next step ─────────────────────────
            history += f"\nThought:{raw_response}\nObservation: {observation}\n"

        if final_answer is None:
            final_answer = "I could not complete the task within the step limit."

        return final_answer

    def _parse_response(self, response: str):
        """
        Extract Thought, tool_name, and tool_input from LLM response.

        Expected format:
          Thought: some reasoning here
          Action: tool_name('input string')
        """
        thought = ""
        tool_name = None
        tool_input = ""

        # Extract thought
        thought_match = re.search(r"Thought:\s*(.+?)(?=Action:|$)", response, re.DOTALL)
        if thought_match:
            thought = thought_match.group(1).strip()

        # Extract action — matches: tool_name('input') or tool_name("input")
        action_match = re.search(r"Action:\s*(\w+)\(['\"](.+?)['\"]\)", response, re.DOTALL)
        if action_match:
            tool_name  = action_match.group(1).strip()
            tool_input = action_match.group(2).strip()
        else:
            # Try without quotes for simple inputs
            action_match2 = re.search(r"Action:\s*(\w+)\((.+?)\)", response, re.DOTALL)
            if action_match2:
                tool_name  = action_match2.group(1).strip()
                tool_input = action_match2.group(2).strip().strip("'\"")

        return thought, tool_name, tool_input

    def _execute_tool(self, tool_name: str, tool_input: str) -> str:
        """Look up the tool and call it with the given input."""
        if tool_name not in TOOLS:
            return f"Error: Tool '{tool_name}' not found. Available: {list(TOOLS.keys())}"

        try:
            tool_fn = TOOLS[tool_name]["function"]
            result  = tool_fn(tool_input)
            return str(result)
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"