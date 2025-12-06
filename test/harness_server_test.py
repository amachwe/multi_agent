# TEST
from lib.harness import serve
from lib.a2a_grpc_util import build_message_response, build_message, extract_message_role_and_parts
from a2a_grpc.a2a_pb2_grpc import A2AServiceServicer
from a2a_grpc.a2a_pb2 import AgentCard, Message, Role
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure file logging for server test
file_handler = logging.FileHandler('harness_server_test.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

class Test_A2A_Server(A2AServiceServicer):
    
    def SendMessage(self, request, context):

        logger.info(f"Test_A2A_Server received SendMessage request - roles: {Role.ROLE_USER}, {Role.ROLE_AGENT}, {Role.ROLE_UNSPECIFIED}")
        id, role, parts = extract_message_role_and_parts(request.request)
        if role == Role.ROLE_AGENT:
            role_name = "Agent"
        elif role == Role.ROLE_USER:
            role_name = "User"
        elif role == Role.ROLE_UNSPECIFIED:
            role_name = "Unspecified"

        logger.info(f"Extracted id: {id}")
        logger.info(f"Extracted role: {role_name}")
        logger.info(f"Extracted parts: {parts}")
        return build_message_response(build_message(id, Role.ROLE_AGENT,f"Test response from agent, {role_name} with parts: {''.join(parts)}"))

    def GetAgentCard(self, request, context):
        logger.info("Test_A2A_Server received GetAgentCard request")

        return AgentCard(
            name="Test Agent",
            description="This is a test agent for unit testing.",
            version="1.0.0"
        )

        

if __name__ == "__main__":
    serve(Test_A2A_Server(), port="50051")