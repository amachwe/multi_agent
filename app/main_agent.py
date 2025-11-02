from google.adk.agents import LlmAgent

MODEL="gemini-2.5-flash"

instructions="""
You provide information by consulting other agents via available tools.
You will be given a discovery of agents and their capabilities via a tool.
"""

agent = LlmAgent(
    name="Lead_Agent",
    model=MODEL,
    description="An agent that leads the task resoluton by coordinating with other agents",
    instruction=instructions
)


root_agent = agent