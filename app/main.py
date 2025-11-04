import lib.harness as harness
import lib.a2a_grpc_util as a2a_grpc_util
import a2a_grpc.a2a_pb2 as a2a_proto
from a2a_grpc.a2a_pb2_grpc import A2AServiceServicer
from .main_agent import root_agent
from google.genai.types import Content 

from .lg_greeter import get_lg_greeter
from google.protobuf import json_format

EMPTY_RESPONSE = Content(role="model", parts=[])


DEFAULT_AGENT = "<DEF>"
AGENT_MAP = {
    "adk_greeter": (root_agent, harness.run_adk_agent),
    "lg_greeter": (get_lg_greeter(), harness.run_lg_agent),
    DEFAULT_AGENT: (root_agent, harness.run_adk_agent)
}

def map_to_agent(name:str):
   return AGENT_MAP.get(name, AGENT_MAP.get(DEFAULT_AGENT))

class AgentMain(A2AServiceServicer):

    def SendMessage(self, request, context):
        print("AgentMain received SendMessage request", request)
        content = a2a_grpc_util.map_message_to_agent_content(request.request)
        print("Mapped content:", content,"<<")
        #something comes here... where we run either LG or ADK agent.
        
        metadata = json_format.MessageToDict(request.request.metadata)
        
        agent_name = metadata.get("agent_name","<DEF>")
        print(metadata, agent_name,"....")
        agent, runner = map_to_agent(agent_name)
        response = runner("app:main:AgentMain", "1002", "1", content, agent)
        print(response,"<<")
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