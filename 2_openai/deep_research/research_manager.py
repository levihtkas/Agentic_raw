from typing import Any


from dis import Instruction
from agents import Agent,Runner,trace
from search_agent import search_agent
from planner_agent import planner_agent

class ResearchManager:
    def __init__(self) -> None:
        tools = [planner_agent.as_tool(tool_name="planning_tool",tool_description="Use this to get additional queries or additional information from the user."),search_agent.as_tool(tool_name="searching_tool",tool_description="Use this to search the web for the queries.")]
        instruction= "You are an orchestrator. You need to understand the user query, and then you need to decide whether to pass it on to the planning tool to get the input from the user or to get additional queries, or else you need to go for the search tool. The search tool will search the web and internet and give you the top three results, and then with that you need to answer the user."
        self.research = Agent[Any](name="Research manager",instructions=instruction,model="gpt-4o-mini",tools=tools)
    async def run(self,query:str):
        with trace("Research Trace"):
            print("Agent Started")
            result = await Runner.run(self.research,query)
            return result.final_output