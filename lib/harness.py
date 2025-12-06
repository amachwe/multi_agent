from google.adk.runners import Runner
from google.adk.agents import Agent
from google.adk.sessions import Session, InMemorySessionService
import google.genai.types as types
import lib.memory as memory
from langgraph.graph import StateGraph


import logging

import grpc
from concurrent import futures
from a2a_grpc import a2a_pb2_grpc, a2a_pb2
from lib import a2a_grpc_util 
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure file logging for harness
file_handler = logging.FileHandler('harness.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

session_service = InMemorySessionService()



def run_adk_agent(app_name: str, session_id:str, user_id:str, incoming: types.Content , agent: Agent)-> types.Content:
    
    async def inner():
        name = agent.name
        
        memory_snapshot = memory.load_from_memory(user_id, session_id)
        state = {
            "memory_snapshot": memory_snapshot
        }
        logger.debug("--------")
        logger.info(f"Creating session with state: {state}")
        logger.debug("--------")
        current_session = await session_service.create_session(app_name=app_name, session_id=session_id, user_id=user_id, state=state)
        #agent / llm error handling
        runner = Runner(app_name=app_name, agent=agent.root_agent, session_service=session_service)
        
        async for response in runner.run_async(
            session_id=session_id,
            user_id=user_id,
            new_message=incoming
        ):
            logger.debug(f">> Runner response: {response}<<")
            if response.is_final_response() and response.content and response.content.parts:
                logger.info(f"Received response: {response}")
                
                return response.content
            
        
        
    return asyncio.run(inner())

def run_lg_agent(app_name: str, session_id:str, user_id:str, incoming: types.Content , graph: StateGraph)-> types.Content:

    #add something for session/state management
    compiled = graph.compile()
    logger.info(f"Incoming: {incoming}")
    memory_snapshot = memory.load_from_memory(user_id, session_id)
   
    if incoming.role == a2a_grpc_util.CONTENT_ROLE_HUMAN:
        request = {
            "request":incoming.parts[0].text,
            "memory_snapshot": memory_snapshot
        }
        
        response = compiled.invoke(request)
        logger.info(f"Received response: {response}")
 
        content = types.Content(role=a2a_grpc_util.CONTENT_ROLE_AGENT, parts=[types.Part(text=response.get("response","NO AGENT RESPONSE"))])
        return content
        
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
    logger.info(f"Server started on port {port}")
    server.wait_for_termination()


def get_agent_stub(server_address:str):
    channel = grpc.insecure_channel(server_address)
    stub = a2a_pb2_grpc.A2AServiceStub(channel)
    return stub