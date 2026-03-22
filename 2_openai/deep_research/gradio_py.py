import gradio as gr
from planner_agent import planner_agent
from agents import Agent,trace,Runner
from research_manager import ResearchManager

async def ChatInterface(message,history):
    messages= []
    for i in history:
        messages.append({'role':i['role'],'content':i['content']})
    messages.append({'role':'user','content':message})
    if len(history)==0:
        with trace("Planner with Questions"):
            result = await ResearchManager().run(messages)
    else:
        result = await ResearchManager().run(messages)
    print(result)

    return result

    ans = result

    if ans.status == "ask_user":
        # show one question to the user
        
        question = ('\n').join(ans.questions) if ans.questions else "Could you clarify a bit more?"

        return question

    # otherwise show the research plan nicely
    if ans.status == "research":
        if not ans.searches:
            return "I have enough information, but I did not generate any searches."
        
        lines = []
        for i, search in enumerate(ans.searches, 1):
            lines.append(f"{i}. {search.query}\nReason: {search.reason}")
        return "\n\n".join(lines)

    return "I could not determine the next step."

demo = gr.ChatInterface(fn=ChatInterface,type="messages")
if __name__ == "__main__":
    demo.launch()