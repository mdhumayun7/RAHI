"""
RAHI ReAct Reasoning Engine
============================
Paper: "ReAct: Synergizing Reasoning and Acting in Language Models"
       Yao et al., 2022 — https://arxiv.org/abs/2210.03629
"""

import re
from brain.llm_client import get_llm_response
from brain.tools import TOOLS, get_tools_description


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


class ReActEngine:

    def __init__(self, max_steps: int = 6, verbose: bool = True):
        self.max_steps = max_steps
        self.verbose   = verbose

    def run(self, goal: str) -> str:
        history = ""
        final_answer = None

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"🎯 GOAL: {goal}")
            print(f"{'='*60}")

        for step in range(1, self.max_steps + 1):
            if self.verbose:
                print(f"\n--- Step {step} ---")

            system = REACT_SYSTEM_PROMPT.format(tools=get_tools_description())
            user   = REACT_USER_TEMPLATE.format(goal=goal, history=history)

            raw_response = get_llm_response(prompt=user, system=system)
            full_response = "Thought:" + raw_response

            if self.verbose:
                print(full_response)

            thought, tool_name, tool_input = self._parse_response(full_response)

            if not tool_name:
                if self.verbose:
                    print("⚠️  Could not parse action. Stopping.")
                break

            observation = self._execute_tool(tool_name, tool_input)

            if self.verbose:
                print(f"🔍 Observation: {observation}")

            if tool_name == "finish":
                final_answer = observation
                if self.verbose:
                    print(f"\n{'='*60}")
                    print(f"✅ FINAL ANSWER: {final_answer}")
                    print(f"{'='*60}")
                break

            history += f"\nThought:{raw_response}\nObservation: {observation}\n"

        if final_answer is None:
            final_answer = "I could not complete the task within the step limit."

        return final_answer

    def _parse_response(self, response: str, attempt: int = 1):
        """Parse with self-correction."""
        thought = ""
        tool_name = None
        tool_input = ""

        thought_match = re.search(r"Thought:\s*(.+?)(?=Action:|$)", response, re.DOTALL)
        if thought_match:
            thought = thought_match.group(1).strip()

        action_match = re.search(r"Action:\s*(\w+)\(['\"](.+?)['\"]\)", response, re.DOTALL)
        if action_match:
            tool_name  = action_match.group(1).strip()
            tool_input = action_match.group(2).strip()
        else:
            action_match2 = re.search(r"Action:\s*(\w+)\((.+?)\)", response, re.DOTALL)
            if action_match2:
                tool_name  = action_match2.group(1).strip()
                tool_input = action_match2.group(2).strip().strip("'\"")

        if not tool_name and attempt <= 2:
            if self.verbose:
                print(f"⚠️  Parse failed (attempt {attempt}) — self-correcting...")

            correction_prompt = f"""Your previous response had incorrect format.

Previous response: {response}

You MUST follow this EXACT format:
Thought: [your reasoning]
Action: tool_name('input')

Available tools: {list(TOOLS.keys())}

Try again with correct format:
Thought:"""

            corrected = get_llm_response(prompt=correction_prompt)
            corrected_full = "Thought:" + corrected
            if self.verbose:
                print(f"🔄 Corrected: {corrected_full[:100]}")
            return self._parse_response(corrected_full, attempt + 1)

        if tool_name and tool_name not in TOOLS:
            if self.verbose:
                print(f"⚠️  Unknown tool '{tool_name}' — self-correcting...")
            tool_name = None
            return self._parse_response(response, attempt + 1)

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