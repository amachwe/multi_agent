from langgraph.graph import StateGraph, START, END
from gen_ai_web_server import llm_client
from lib.server_build import run_server
from lib.harness import get_agent_card, run_lg_agent
import pydantic
from typing import Dict
import logging
import os
import a2a_grpc.a2a_pb2 as a2a_proto
from langchain_ollama import OllamaLLM



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Ensure log directory exists
os.makedirs('log', exist_ok=True)

AGENT_NAME = "basic_greeter"

# Configure file logging for lg_greeter
file_handler = logging.FileHandler('log/lg_greeter.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)


client = llm_client.Client()
model = OllamaLLM(model="phi4-mini", temperature=0.0)

class State(pydantic.BaseModel):
    request: str
    memory_snapshot: str = ""
    response: str = ""



graph = StateGraph(State)

def say_hi(state: State)->State:
    # response = client.send_request(
    #     prompt=[
            
    #         {"role":"user","content":f"You are a helpful assistant. User's input: {state.request}\n\n## Use the following memory context:\n{state.memory_snapshot}"}
    #     ]
    # )
    response = model.invoke(f"You are a helpful assistant. User's input: {state.request}\n\n## Use the following memory context:\n{state.memory_snapshot}")
    logger.info(f"LG LLM Response: {response.encode('utf-8')}")
    try:
        state.response = response
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

def get_agent_card()->a2a_proto.AgentCard:
    card = a2a_proto.AgentCard(
        name=AGENT_NAME,
        description="An agent that answers questions",
        skills=[
                a2a_proto.AgentSkill(name="answer", description="Answer questions.")]
        
    )
    return card


if __name__ == "__main__":

    from lib.server_build import run_server, AgentPackage
    from lib.harness import run_lg_agent

    package = AgentPackage(
        name=AGENT_NAME,
        agent_code=get_lg_greeter(),
        agent_card=get_agent_card()
    )
    
    run_server(run_lg_agent,package)


