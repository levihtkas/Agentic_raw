# imports

from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr


# The usual start

load_dotenv(override=True)
openai = OpenAI()

# For pushover

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

def push(message):
    print(f"{message}")
    payload = {"user":pushover_user,"token":pushover_token,"message":message}
    requests.post(pushover_url,data=payload)

def record_user_details(email,name="N/A",notes="N/1"):
    push(f"Recording interest from {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question} asked that I couldn't answer")
    return {"recorded": "ok"}

#Now time for json so our LLM So LLM knows that a particular tool exists.
record_user_details_json = {
    "name": "record_user_details",
    "description":"choose this tool if someone wants to contact me or says that or has an interest in contacting me. You just ask them their name, email, and notes, and call this tool.",
    "parameters":{
        "type": "object",
        "properties":{
            "email":{
                "type":"string",
                "description":"the email address of the user"
            },
            "name":{
                "type":"string",
                "description":"the name of the user"
            },
            "notes":{
                "type":"string",
                "description":"Any additional information on why they want to contact us?"
            }
        },
        "required":['email','name','notes']
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

class Me:
    tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json}]
    def __init__(self):
        self.openai=OpenAI()
        self.user_text = ""
        pdf_reader = PdfReader('./me/resume.pdf')
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                self.user_text+=text
        
    @staticmethod
    def handle_tool_call(tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}")
            result = globals().get(tool_name)(**arguments)
            results.append({'role':'tool','content':json.dumps(result),"tool_call_id":tool_call.id})
        return results
    
    def system_prompt(self):
        name="Vijayalakshmi B"
        system_prompt = f"You are acting as {name}. You are answering questions on {name}'s website, \
        particularly questions related to {name}'s career, background, skills and experience. \
        Your responsibility is to represent {name} for interactions on the website as faithfully as possible. \
        You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions. \
        Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
        If you don't know the answer, say so."

        system_prompt += f"\n\n## {self.user_text}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {name}."
        return system_prompt

    
    def chat(self,message,history):
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        done = False
        while not done:
            response = openai.chat.completions.create(model="gpt-4o-mini",messages=messages,tools=Me.tools)
            if response.choices[0].finish_reason == "tool_calls":
                tool_calls = response.choices[0].message.tool_calls
                results = Me.handle_tool_call(tool_calls)
                print(response.choices[0].message)
                messages.append(response.choices[0].message)
                messages.extend(results)
            else:
                done=True
        return response.choices[0].message.content




    

if __name__ == "__main__":
    me=Me()
    gr.ChatInterface(me.chat, type="messages").launch()
