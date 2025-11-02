import lib.harness as harness
import lib.a2a_grpc_util as a2a_grpc_util
import a2a_grpc.a2a_pb2 as a2a_proto
from a2a_grpc.a2a_pb2_grpc import A2AServiceServicer
from .main_agent import root_agent
import asyncio

class AgentMain(A2AServiceServicer):

    def SendMessage(self, request, context):
        print("AgentMain received SendMessage request", request)
        content = a2a_grpc_util.map_message_to_agent_content(request.request)
        print("Mapped content:", content)

        response = asyncio.run(harness.run_agent("app.main:AgentMain","1002","1",content,root_agent))
        print(response)
        message = a2a_grpc_util.build_message_from_parts(request.request.message_id, a2a_proto.Role.ROLE_AGENT , response.content.parts)
        return a2a_grpc_util.build_agent_message_response(request.request.message_id, message)    

    def GetAgentCard(self, request, context):
        card = a2a_proto.AgentCard(
            name="MainAgent",
            description="This is the main agent handling requests."
        )

        return card


if __name__ == "__main__":

 harness.serve(AgentMain(), port="50051")