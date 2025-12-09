from langgraph.graph import StateGraph, START, END
from gen_ai_web_server import llm_client

import pydantic
from typing import Dict
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Ensure log directory exists
os.makedirs('log', exist_ok=True)

# Configure file logging for lg_greeter
file_handler = logging.FileHandler('log/lg_greeter.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

client = llm_client.Client()

class State(pydantic.BaseModel):
    request: str
    memory_snapshot: str = ""
    response: str = ""

graph = StateGraph(State)

def say_hi(state: State)->State:
    response = client.send_request(
        prompt=[
            
            {"role":"user","content":f"You are a helpful assistant. User's input: {state.request}\n\n## Use the following memory context:\n{state.memory_snapshot}"}
        ]
    )
    logger.info(f"LG LLM Response: {client.extract_response(response)}")
    try:
        state.response = client.extract_response(response)
    except Exception as e:
        logger.error(f"Error extracting response: {e}")
        state.response = "I'm sorry, I couldn't process your request."
    return state

#build the LG Graph - a single interaction more like an LLM call - no agents here... just pretending to be one!
graph.add_node(say_hi)
graph.add_edge(START, "say_hi")
graph.add_edge("say_hi",END)

def get_lg_greeter()->StateGraph:
    return graph



if __name__ == "__main__":

    request = State(request="what is 2+2?") 
    print(graph.compile().invoke(request))


