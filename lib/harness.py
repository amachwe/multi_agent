from google.adk.runners import Runner
from google.adk.agents import Agent
from google.adk.sessions import Session, InMemorySessionService
import google.genai.types as types
import logging

import grpc
from concurrent import futures
from a2a_grpc import a2a_pb2_grpc, a2a_pb2  

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

session_service = InMemorySessionService()


async def run_agent(app_name: str, session_id:str, user_id:str, incoming: types.Content , agent: Agent)-> types.Content:
    name = agent.name
    
    current_session = await session_service.create_session(app_name=app_name, session_id=session_id, user_id=user_id)
       
    runner = Runner(app_name=app_name, agent=agent.root_agent, session_service=session_service)

    async for response in runner.run_async(
        session_id=session_id,
        user_id=user_id,
        new_message=incoming
    ):
        if response.is_final_response() and response.content and response.content.parts:
            logger.debug(f"Received response: {response}")
            return response.content
        
def send_message(request, server_address:str): 
    stub = get_agent_stub(server_address)
    response = stub.SendMessage(request)
    return response

def get_agent_card(request:a2a_pb2.GetAgentCardRequest, server_address:str):
    stub = get_agent_stub(server_address)
    response = stub.GetAgentCard(a2a_pb2.GetAgentCardRequest())
    return response

def serve(servicer: a2a_pb2_grpc.A2AServiceServicer,port:str):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    a2a_pb2_grpc.add_A2AServiceServicer_to_server(servicer, server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Server started on port {port}")
    server.wait_for_termination()


def get_agent_stub(server_address:str):
    channel = grpc.insecure_channel(server_address)
    stub = a2a_pb2_grpc.A2AServiceStub(channel)
    return stub