from langgraph.graph import StateGraph, START, END
from gen_ai_web_server import llm_client
import a2a_grpc.a2a_pb2 as a2a_proto


import pydantic
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

AGENT_NAME = "idontknow"


# Ensure log directory exists
os.makedirs('log', exist_ok=True)

# Configure file logging for enemy_mover
file_handler = logging.FileHandler('log/idontknow.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

client = llm_client.Client()

class State(pydantic.BaseModel):
    request: str
    memory_snapshot: str = ""
    response: str = ""

graph = StateGraph(State)

def idk(state: State)->State:
    response = client.send_request(
        prompt=[
            
            {"role":"user","content":f"You ALWAYS RESPOND WITH I DON'T KNOW TO ANY USER INPUT. "}
        ]
    )
    logger.info(f"IDK LLM Response: {client.extract_response(response)}")
    try:
        state.response = client.extract_response(response)
    except Exception as e:
        logger.error(f"Error extracting response: {e}")
        state.response = "I'm sorry, I couldn't process your request."
    return state

#build the LG Graph - a single interaction more like an LLM call - no agents here... just pretending to be one!
graph.add_node(idk)
graph.add_edge(START, "idk")
graph.add_edge("idk",END)

def get_agent()->StateGraph:
    return graph

def get_agent_card()->a2a_proto.AgentCard:
    card = a2a_proto.AgentCard(
        name=AGENT_NAME,
        description="An agent that processes data.",
        skills=[ 
                a2a_proto.AgentSkill(name="process_currency_request", description="Answer questions about currency exchange rates."),],
        
    )
    return card



if __name__ == "__main__":
    from lib.server_build import run_server, AgentPackage
    from lib.harness import run_lg_agent


    package = AgentPackage(
        name=AGENT_NAME,
        agent_code=get_agent(),
        agent_card=get_agent_card()
    )
    run_server(run_lg_agent,package)
    # request = State(request="what is 2+2?") 
    # print(graph.compile().invoke(request))


