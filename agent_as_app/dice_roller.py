from langgraph.graph import StateGraph, START, END
from gen_ai_web_server import llm_client
import a2a_grpc.a2a_pb2 as a2a_proto


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

def get_agent_card()->a2a_proto.AgentCard:
    card = a2a_proto.AgentCard(
        name=AGENT_NAME,
        description="A dice rolling agent that simulates rolling a 6-sided die.",
        skills=[a2a_proto.AgentSkill(name="roll_dice", description="Roll a 6-sided die and return the result."), 
                a2a_proto.AgentSkill(name="answer", description="Answer questions.")],
        
    )
    return card



if __name__ == "__main__":
    from lib.server_build import run_server, AgentPackage
    from lib.harness import run_lg_agent


    package = AgentPackage(
        name=AGENT_NAME,
        agent_code=get_dice_roller(),
        agent_card=get_agent_card(),
        port="50051"
    )
    run_server(run_lg_agent,package)
    # request = State(request="what is 2+2?") 
    # print(graph.compile().invoke(request))


