import lib.harness as harness
import lib.a2a_grpc_util as a2a_grpc_util
import a2a_grpc.a2a_pb2 as a2a_proto
from a2a_grpc.a2a_pb2_grpc import A2AServiceServicer
from .main_agent import root_agent
from google.genai.types import Content 
import lib.memory as memory

from .lg_greeter import get_lg_greeter
from .dice_roller import get_dice_roller
from google.protobuf import json_format

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, filemode='w', filename='agent_runner_server.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

EMPTY_RESPONSE = Content(role="model", parts=[])


DEFAULT_AGENT = "<DEF>"
AGENT_MAP = {
    "adk_greeter": (root_agent, harness.run_adk_agent),
    "lg_greeter": (get_lg_greeter(), harness.run_lg_agent),
    "dice": (get_dice_roller(), harness.run_lg_agent),  # Using LG agent for dice roller as well
    DEFAULT_AGENT: (root_agent, harness.run_adk_agent)
}

def map_to_agent(name:str):
   return AGENT_MAP.get(name, AGENT_MAP.get(DEFAULT_AGENT))

class AgentMain(A2AServiceServicer):

    def SendMessage(self, request, context):
        logger.info(f"AgentMain received SendMessage request {request}")
        content = a2a_grpc_util.map_message_to_agent_content(request.request)
        logger.info(f"Mapped content: {content} <<")
        #something comes here... where we run either LG or ADK agent.
        
        metadata = json_format.MessageToDict(request.request.metadata)
        
        agent_name = metadata.get("agent_name","<DEFAULT>")
        user_id = metadata.get("user_id","X")
        session_id = metadata.get("session_id","X")
        logger.info(f"Metadata: {metadata}")
        agent, runner = map_to_agent(agent_name)
        memory.set_user_memory(user_id, session_id, content.parts[0].text)
        response = runner("app:main:AgentMain", session_id, user_id, content, agent)
        memory.set_agent_memory(user_id, session_id, response.parts[0].text)
        
        if response is None:
           response = EMPTY_RESPONSE
        message = a2a_grpc_util.build_message_from_parts(request.request.message_id, a2a_proto.Role.ROLE_AGENT , a2a_grpc_util.genai_part_to_proto_part(response.parts))
        return a2a_grpc_util.build_message_response( message)    

    def GetAgentCard(self, request, context):
        card = a2a_proto.AgentCard(
            name="MainAgent",
            description="This is the main agent handling requests."
        )

        return card


if __name__ == "__main__":

 harness.serve(AgentMain(), port="50051")