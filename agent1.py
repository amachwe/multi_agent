import a2a_grpc.a2a_pb2_grpc as a2a_grpc
import a2a_grpc.a2a_pb2 as a2a_proto
import grpc
from concurrent import futures
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure file logging for agent1
file_handler = logging.FileHandler('agent1.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)


def build_agent_message_response(id:str, message: str) -> a2a_proto.Message:
    message = a2a_proto.Message(
        message_id=id,
        role=a2a_proto.Role.ROLE_AGENT,
        parts = [a2a_proto.Part(text=message)]

    )
    return a2a_proto.SendMessageResponse(msg=message)

class Agent1(a2a_grpc.A2AServiceServicer):
    
    def SendMessage(self, request, context):
        logger.info(f"Agent1 received SendMessage - request: {request}, context: {context}")

        response = build_agent_message_response(request.request.message_id, f"Agent1 received: {request}")
        return response
    
    def SendStreamingMessage(self, request, context):
        logger.info(f"Agent1 received SendStreamingMessage - request: {request}, context: {context}")
        for i in range(3):
            response = build_agent_message_response(request.request.message_id, f"Agent1 streaming part {i+1} for: {request}")
            yield response
    
def serve(port="50051"):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    a2a_grpc.add_A2AServiceServicer_to_server(Agent1(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info(f"Server started on port {port}")
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filemode='w', filename='agent1_main.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    serve()
