import grpc 
from a2a_grpc import a2a_pb2_grpc as a2a_grpc
from a2a_grpc import a2a_pb2 as a2a_proto
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure file logging for agent2
file_handler = logging.FileHandler('agent2.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

def build_agent_message_request(id:str, message: str) -> a2a_proto.Message:
    message = a2a_proto.Message(
        message_id=id,
        role=a2a_proto.Role.ROLE_AGENT,
        parts = [a2a_proto.Part(text=message)]

    )
    return a2a_proto.SendMessageRequest(request=message)
 

def client_run():
    message = "Hello from Agent2"
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = a2a_grpc.A2AServiceStub(channel)
        request = build_agent_message_request("agent2", message)
        response = stub.SendStreamingMessage(request)
        for part in response:
            logger.info(f"Agent2 received: {part}")



if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, filemode='w', filename='agent2_main.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    client_run()