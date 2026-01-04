from langgraph.graph import StateGraph, START, END
from gen_ai_web_server import llm_client
import a2a_grpc.a2a_pb2 as a2a_proto


import pydantic
from typing import Dict
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

AGENT_NAME = "enemy_mover"

enemies = """
You are enemy AI. 

Dark Elves - jump and attack from above.
Orcs - charge directly at the player.
Goblins - use hit-and-run tactics.
"""

# Ensure log directory exists
os.makedirs('log', exist_ok=True)

# Configure file logging for enemy_mover
file_handler = logging.FileHandler('log/enemy_mover.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

client = llm_client.Client()

class State(pydantic.BaseModel):
    request: str
    memory_snapshot: str = ""
    response: str = ""

graph = StateGraph(State)

def move_enemy(state: State)->State:
    response = client.send_request(
        prompt=[
            
            {"role":"user","content":f"You represent enemies in a game (dungeon master). You always respond to the user and are responsible for moving enemies that are engaged or to give list of enemies. Enemy attack behaviour below: {enemies}. User's input: {state.request}\n\n## Use the following memory context:\n{state.memory_snapshot}"}
        ]
    )
    logger.info(f"Enemy LLM Response: {client.extract_response(response)}")
    try:
        state.response = client.extract_response(response)
    except Exception as e:
        logger.error(f"Error extracting response: {e}")
        state.response = "I'm sorry, I couldn't process your request."
    return state

#build the LG Graph - a single interaction more like an LLM call - no agents here... just pretending to be one!
graph.add_node(move_enemy)
graph.add_edge(START, "move_enemy")
graph.add_edge("move_enemy",END)

def get_enemy_mover()->StateGraph:
    return graph

def get_agent_card()->a2a_proto.AgentCard:
    card = a2a_proto.AgentCard(
        name=AGENT_NAME,
        description="A dungeon master agent. Enemy mover that controls enemy movements based on their behavior.",
        skills=[a2a_proto.AgentSkill(name="move_enemy", description="Move enemies according to their behavior."), 
                a2a_proto.AgentSkill(name="answer", description="Answer questions.")],
        
    )
    return card



if __name__ == "__main__":
    from lib.server_build import run_server, AgentPackage
    from lib.harness import run_lg_agent


    package = AgentPackage(
        name=AGENT_NAME,
        agent_code=get_enemy_mover(),
        agent_card=get_agent_card(),
        port="50054"
    )
    run_server(run_lg_agent,package)
    # request = State(request="what is 2+2?") 
    # print(graph.compile().invoke(request))


