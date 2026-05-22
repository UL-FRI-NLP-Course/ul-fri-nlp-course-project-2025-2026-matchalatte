from smolagents import (
    CodeAgent,
    TransformersModel,
    DuckDuckGoSearchTool,
    FinalAnswerTool,
)
from agents import search_train_connections, weather_forecast

model = TransformersModel(
    model_id="meta-llama/Llama-3.1-8B-Instruct",
    device_map="auto",
)

agent = CodeAgent(
    tools=[
        search_train_connections,
        weather_forecast,
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
"""
)

prompts = [
    "When is the earliest train from Ljubljana to Milano today?",
    "What will the weather be like in Barcelona for the next 3 days?",
    "Can you suggest a romantic weekend in Europe for a couple?",
    "What clothes should I pack for the next 3 days in Rome?",
    "I’m visiting Barcelona with friends for 3 days and we want beaches, nightlife, and fun activities. What should we do?"
]

results = []
for prompt in prompts:
    results.append((prompt, agent.run(prompt)))

print("======= RESULTS =======\n")
for prompt, result in results:
    print(prompt)
    print(result, '\n')
print("=======================")