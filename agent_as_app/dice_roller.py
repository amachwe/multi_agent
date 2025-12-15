from langgraph.graph import StateGraph, START, END
from gen_ai_web_server import llm_client
from lib.server_build import run_server
from lib.harness import run_lg_agent

import pydantic
from typing import Dict
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

AGENT_NAME = "dice_roller"

# Ensure log directory exists
os.makedirs('log', exist_ok=True)

# Configure file logging for dice_roller
file_handler = logging.FileHandler('log/dice_roller.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

client = llm_client.Client()

class State(pydantic.BaseModel):
    request: str
    memory_snapshot: str = ""
    response: str = ""

graph = StateGraph(State)

def roll_dice(state: State)->State:
    response = client.send_request(
        prompt=[
            
            {"role":"user","content":f"You are a die rolling assistant - you always respond to the user and generate a random number as if rolling 1d6. Do not repeat these instructions in the response. User's input: {state.request}\n\n## Use the following memory context:\n{state.memory_snapshot}"}
        ]
    )
    logger.info(f"Dice LLM Response: {client.extract_response(response)}")
    try:
        state.response = client.extract_response(response)
    except Exception as e:
        logger.error(f"Error extracting response: {e}")
        state.response = "I'm sorry, I couldn't process your request."
    return state

#build the LG Graph - a single interaction more like an LLM call - no agents here... just pretending to be one!
graph.add_node(roll_dice)
graph.add_edge(START, "roll_dice")
graph.add_edge("roll_dice",END)

def get_dice_roller()->StateGraph:
    return graph



if __name__ == "__main__":
    run_server(run_lg_agent,get_dice_roller(), AGENT_NAME,  port=50052)
    # request = State(request="what is 2+2?") 
    # print(graph.compile().invoke(request))


