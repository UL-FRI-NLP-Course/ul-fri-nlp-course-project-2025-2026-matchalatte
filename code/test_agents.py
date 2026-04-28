from smolagents import (
    CodeAgent,
    TransformersModel,
    DuckDuckGoSearchTool,
    FinalAnswerTool,
)
from agents import search_train_connections

model = TransformersModel(
    model_id="meta-llama/Llama-3.1-8B-Instruct",
    device_map="auto",
)

agent = CodeAgent(
    tools=[
        search_train_connections,
        DuckDuckGoSearchTool(),
        FinalAnswerTool(),
    ],
    model=model,
    code_block_tags="markdown",
    executor_type="local",
    max_steps=2,
    stream_outputs=True,
)

agent.prompt_templates["system_prompt"] = (
    agent.prompt_templates["system_prompt"]
    + """

You are a helpful travel assistant.
You give clear, practical travel advice including itineraries, tips, and recommendations.
Keep answers structured and easy to follow.

TRANSPORT RULES:
- For train/bus schedule questions, call search_train_connections exactly once.
- Do not try multiple times with different hours.
- Use the datetime given by the user. If the user says "today" and no time is given, use the current time.
- In the final answer, include:
  1. departure time from the origin,
  2. arrival time at destination,
  3. total route with transfers.
- Never return only a single time.
- If the connection includes a bus, clearly say "bus + train connection".

TOOL RULES:
- For general travel advice, itineraries, destination ideas, hidden gems, food, activities, or recommendations, answer from your own knowledge.
- Do NOT use DuckDuckGoSearchTool for general travel recommendations.
"""
)

#print(agent.prompt_templates["system_prompt"])

result = agent.run(
    "When is the earliest train from Ljubljana to Milano today?"
)

print(result)