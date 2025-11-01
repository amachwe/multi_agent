# TEST
from lib.harness import serve
from lib.a2a_grpc_util import build_agent_message_response, extract_message_role_and_parts
from a2a_grpc.a2a_pb2_grpc import A2AServiceServicer
from a2a_grpc.a2a_pb2 import AgentCard


class Test_A2A_Server(A2AServiceServicer):
    
    def SendMessage(self, request, context):
        print("Test_A2A_Server received SendMessage request")
        role, parts = extract_message_role_and_parts(request.request)
        print("Extracted role:", role)
        print("Extracted parts:", parts)
        return build_agent_message_response(request.message_id, "Test response from agent "+ role + "  with parts: " + ", ".join(parts))
    
    def GetAgentCard(self, request, context):
        print("Test_A2A_Server received GetAgentCard request")

        return AgentCard(
            name="Test Agent",
            description="This is a test agent for unit testing.",
            version="1.0.0"
        )

        

if __name__ == "__main__":
    serve(Test_A2A_Server(), port="50051")