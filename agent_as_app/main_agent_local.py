from langgraph.graph import StateGraph, START, END
from langchain.agents import create_agent
from gen_ai_web_server import llm_client
from lib.server_build import run_server
from lib.harness import get_agent_card, run_lg_agent
import pydantic
from typing import Dict
import logging
import os
import a2a_grpc.a2a_pb2 as a2a_proto
from lib.utils import build_instructions_for_agents
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from google.protobuf import struct_pb2
from lib.harness import send_message
from lib.a2a_grpc_util import build_message, build_message_request#
from a2a_grpc.a2a_pb2 import Role


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Ensure log directory exists
os.makedirs('log', exist_ok=True)

AGENT_NAME = "main_agent_local"

# Configure file logging for lg_greeter
file_handler = logging.FileHandler('log/main_agent_local.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

agent_instructions, agent_dict = build_instructions_for_agents()

@tool
def contact_agent(agent_name: str, question: str) -> str:
    """
    Contact another agent by name and ask a question.
    agent_name - string name of the agent to contact
    question - string question to ask the agent
    """
    metadata = struct_pb2.Struct()

    if agent_dict is None:
        return f"No agents found"

    logger.info(f"Contacting agent {agent_name} with question: {question}")
    target_agent = agent_dict.get(agent_name)
    
    if not target_agent:
        return f"Agent {agent_name} not found."
        
    # This is a placeholder implementation. In a real scenario, this would involve making a gRPC call to the other agent.
    try:
        
        user_message = build_message_request(build_message("a2a_request_1", Role.ROLE_USER, question, metadata=metadata))
        
        response = send_message(request=user_message, server_address=f"{target_agent.get('host')}:{target_agent.get('port')}")
        agent_response = response.msg.parts[0].text
        logger.info(f"Received response from agent {agent_name}: {agent_response}")
        return agent_response
    except Exception as e:
        logger.error(f"Error contacting agent {agent_name}: {e}", exc_info=True, stack_info=True)
        return f"Error contacting agent {agent_name}: {str(e)}"


model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")#ChatOllama(model="phi4-mini", temperature=0.0)

agent = create_agent(name=AGENT_NAME, model=model, system_prompt=f"You are a helpful assistant. Use the agents below with the 'contact agent' tool to assist with user queries:  {agent_instructions}", tools=[contact_agent])

class State(pydantic.BaseModel):
    request: str
    memory_snapshot: str = ""
    response: str = ""



graph = StateGraph(State)

def run_agent(state: State)->State:

    instructions = f"You are a helpful assistant. User's input: {state.request}\n\n## Use the following memory context:\n{state.memory_snapshot}"

    try:
        response = agent.invoke({"messages": [{"role": "user", "content": instructions}]})
  
        logger.info(f"LG LLM Response: {str(response).encode('utf-8')}")
    
        state.response = response["messages"][-1].content
    except Exception as e:
        logger.error(f"Error extracting response: {e}", exc_info=True, stack_info=True)  # This prints the full stacktrace
        state.response = "I'm sorry, I couldn't process your request."
    return state

#build the LG Graph - a single interaction more like an LLM call - no agents here... just pretending to be one!
graph.add_node(run_agent)
graph.add_edge(START, "run_agent")
graph.add_edge("run_agent",END)

def get_agent()->StateGraph:
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
        agent_code=get_agent(),
        agent_card=get_agent_card()
    )
    
    run_server(run_lg_agent,package)


