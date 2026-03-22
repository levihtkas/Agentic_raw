from pydantic import BaseModel, Field
from agents import Agent
from typing import Literal

no_of_searches = 3

class WebResults(BaseModel):
    query:str = Field(description="Questions")
    reason:str= Field(description="Reason why we want to search this query")

class WebResultPlan(BaseModel):
    status:Literal["ask_user","research"]
    questions:list[str] = Field(default_factory=list)
    missing_fields:list[str] = Field(default_factory=list)
    searches:list[WebResults] = Field(description="The actual plan goes here.")



planner_agent = Agent(name="Planning Agent",instructions="After the user gives the query, you need to plan out how you will proceed." 
"Either you need to give the additional query and the reason why you chose that query for the deep research purpose"
"Or if you want any additional information from the user end, you need to ask the questions and set the status as Ask User."
 "You can ask what and all fields you need in the missing field section. If you want, you can use the missing field section.",
model="gpt-4o-mini",
output_type=WebResultPlan)




