from google.adk.agents import LlmAgent
from google.adk.models import  LlmRequest
from google.adk.agents.callback_context import CallbackContext
from lib.a2a_grpc_util import build_message, build_message_request
from lib.harness import get_agent_card, send_message
import logging
import yfinance
import os
import a2a_grpc.a2a_pb2 as a2a_proto
from lib.utils import build_instructions_for_agents
from a2a_grpc.a2a_pb2 import Role
from google.protobuf import struct_pb2

logging.basicConfig(level=logging.INFO, filemode='w', filename='log/main_agent.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Ensure log directory exists
os.makedirs('log', exist_ok=True)

AGENT_NAME = "greeter_agent"



MODEL="gemini-2.5-flash"




instructions="""
You have memory provided in memory section.
You can answer questions based your knowledge and the memory.
You are a friendly assistant.
"""

agent_instructions, agent_dict = build_instructions_for_agents()
instructions += agent_instructions


def before_model(callback_context: CallbackContext, llm_request: LlmRequest):
    logger.debug("Before model callback")
    logger.debug(f"Current session state: {callback_context}")
    logger.debug("----LlmRequest Details----")
    logger.debug(f"LlmRequest: {llm_request}")
    logger.debug("--------")
    text = llm_request.contents[0].parts[0].text
    llm_request.contents[0].parts[0].text = f"User's input: {text}\n\n## Use the following memory context:\n{callback_context.state.get('memory_snapshot','')}"
    logger.debug(f"LlmRequest: {llm_request}")
    logger.debug("----End of before model callback----")
    
def extract_stock_info(ticker: str) -> dict:
    """
    Extract stock information for a given ticker symbol.
    ticker - string ticker symbol for the stock
    """
    logger.info("--- Extracting stock info ---")
    stock = yfinance.Ticker(ticker)
    return stock.info

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
        
        response = send_message(request=user_message, server_address=target_agent.get("url").replace("http://",""))
        agent_response = response.msg.parts[0].text
        logger.info(f"Received response from agent {agent_name}: {agent_response}")
        return agent_response
    except Exception as e:
        logger.error(f"Error contacting agent {agent_name}: {e}")
        return f"Error contacting agent {agent_name}: {str(e)}"
    

agent = LlmAgent(
    name="Lead_Agent",
    model=MODEL,
    description="An agent that leads the task resoluton by using tools.",
    instruction=instructions,
    before_model_callback=before_model,
    tools=[extract_stock_info, contact_agent]
)

def get_agent_card()->a2a_proto.AgentCard:
    card = a2a_proto.AgentCard(
        name=AGENT_NAME,
        description="An agent that answers questions using Gemini 2.5 Flash model and has access to stock info tool.",
        skills=[
                a2a_proto.AgentSkill(name="answer", description="Answer questions."),
                a2a_proto.AgentSkill(name="extract_stock_info", description="Extract stock information for a given ticker symbol.")]
        
    )
    return card


root_agent = agent

if __name__ == "__main__":
    from lib.server_build import run_server, AgentPackage
    from lib.harness import run_adk_agent

    package = AgentPackage(
        name=AGENT_NAME,
        agent_code=root_agent,
        agent_card=get_agent_card(),
        port="50053"
    )

    run_server(run_adk_agent, package)