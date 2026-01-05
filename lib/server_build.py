import lib.harness as harness
import lib.a2a_grpc_util as a2a_grpc_util
import a2a_grpc.a2a_pb2 as a2a_proto
from a2a_grpc.a2a_pb2_grpc import A2AServiceServicer
from google.genai.types import Content, Part 
import lib.memory as memory
import atexit

from google.protobuf import json_format
import requests
import json
from google.protobuf.json_format import MessageToDict

import logging
import os

# Ensure log directory exists
os.makedirs('log', exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, filemode='w', filename='log/agent_runner_server.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

EMPTY_RESPONSE = Content(role="model", parts=[])
AGENT_REGISTRY_URL = os.getenv("AGENT_REGISTRY_URL","http://127.0.0.1:5006")
START_UNREGISTERED_AGENTS = os.getenv("START_UNREGISTERED_AGENTS","false").lower() == "true"

class AgentPackage(object):
    def __init__(self, name:str, agent_code, agent_card:a2a_proto.AgentCard, host:str="localhost"):
        self.name = name
        self.agent_code = agent_code
        self.agent_card = agent_card 
        self.host = host


    def get_agent_card(self)->a2a_proto.AgentCard:
        return self.agent_card
    
    def get_agent_code(self):
        return self.agent_code
    
    def get_host(self):
        return self.host
    


class AgentMain(A2AServiceServicer):

    def __init__(self, runner, agent, name):
        super().__init__()
        self.runner = runner
        self.agent = agent
        self.name = name
        
        logger.info("AgentMain initialized")

    def SendMessage(self, request, context):
        logger.info(f"AgentMain received SendMessage request {request}")
        content = a2a_grpc_util.map_message_to_agent_content(request.request)
        logger.info(f"Mapped content: {content} <<")
        #something comes here... where we run either LG or ADK agent.
        
        metadata = json_format.MessageToDict(request.request.metadata)
        
        user_id = metadata.get("user_id","X")
        session_id = metadata.get("session_id","X")
        logger.info(f"Metadata: {metadata}")
        memory.set_user_memory(user_id, session_id, content.parts[0].text)
        response = self.runner("app:main:AgentMain", session_id, user_id, content, self.agent.get_agent_code())
        
        # Handle case where response might be None or malformed
        if response and hasattr(response, 'parts') and len(response.parts) > 0:
            memory.set_agent_memory(user_id, session_id, response.parts[0].text)
        else:
            logger.error(f"Invalid response from agent: {response}")
        
        if response is None:
           response = EMPTY_RESPONSE
           
        # Ensure response has the expected structure
        if not hasattr(response, 'parts') or len(response.parts) == 0:
            logger.error(f"Response missing parts: {response}")
            
        message = a2a_grpc_util.build_message_from_parts(request.request.message_id, a2a_proto.Role.ROLE_AGENT , a2a_grpc_util.genai_part_to_proto_part(response.parts))
        logger.info(f"AgentMain sending response message {message}")
        return a2a_grpc_util.build_message_response( message)    

    def GetAgentCard(self, request, context):
        return self.agent.get_agent_card()
    
def register_thyself(agent:AgentPackage)->str:
    agent_card_dict = MessageToDict(agent.get_agent_card(), preserving_proto_field_name=True)
    payload = {
        "name": agent.name,
        "agent_card": agent_card_dict,
        "host": f"{agent.get_host()}"
    }
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(f"{AGENT_REGISTRY_URL}/agents", data=json.dumps(payload), headers=headers)
    if response.status_code == 200 or response.status_code == 201:
        logger.info(f"Successfully registered agent {agent.name} with registry.")
    else:
        logger.error(f"Failed to register agent {agent.name}. Status code: {response.status_code}, Response: {response.text}")
    
    json_response = response.json()

    
    return json_response.get("port", None), json_response.get("id", None)

def run_server(runner, agent:AgentPackage):
    name = agent.name
    registered = False
    try:  
        port, agent_id = register_thyself(agent)
        if not port:
            raise Exception("Agent registration failed, no port returned.")
        registered = True
    except Exception as e:
        logger.error(f"Error registering agent {agent.name}: {e}. Stopping agent server startup as not allowed to run unregistered.")
    
    def shutdown_handler(agent_id=agent_id, agent=agent):
        requests.delete(f"{AGENT_REGISTRY_URL}/agents/remove/{agent_id}")
        logger.info(f"Unregistered agent {agent.name} with ID {agent_id} from registry.")
    atexit.register(shutdown_handler)

    if registered or START_UNREGISTERED_AGENTS:
        print(f"Agent {name} with ID {agent_id} - server starting at {agent.get_host()}:{port}.")
        harness.serve(AgentMain(runner, agent, name), port=port)


    

    

    
if __name__ == "__main__":

    raise Exception("This file is not meant to be run directly.")