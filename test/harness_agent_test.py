# TEST
from lib.harness import get_agent_card, send_message
from lib.a2a_grpc_util import build_message, build_message_request
from a2a_grpc.a2a_pb2 import Role
from google.protobuf import struct_pb2
import random
import argparse
import requests

import logging
import os

# Ensure log directory exists
os.makedirs('log', exist_ok=True)

logging.basicConfig(level=logging.INFO, filemode='w', filename='log/harness_agent_test.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

AGENT_REGISTRY_URL = os.getenv("AGENT_REGISTRY_URL","http://127.0.0.1:5006")

def find_agent_by_name(agent_name: str, agents: list) -> str:

    for agent in agents:
        if agent.get("name","") == agent_name:
            return agent.get("id",None), agent.get("host",None), agent.get("port",None)
            
    return None

if __name__ == "__main__":
 
    id_base = 0

    parser = argparse.ArgumentParser(description='A2A Client Test')
    parser.add_argument('--session', type=str, help='Custom session ID', default=str(random.randint(1000,9999)))
    parser.add_argument('--user', type=str, help='Custom user ID', default=str(random.randint(1,100)))
    parser.add_argument('--registry_server', type=str, help='Registry server', default="localhost:5006")

    session_id = parser.parse_args().session
    user_id = parser.parse_args().user
    registry_server = parser.parse_args().registry_server

    metadata = struct_pb2.Struct()

    while True:
        response = requests.get(f"http://{registry_server}/agents")
        agents = response.json().get("agents",[])
        print(f"Available agents: {[f'{idx}: {agent.get('name','')}' for idx, agent in enumerate(agents)]}")
        main_text = input(f"\n\nType e to exit or agent id to connect): ")
        if main_text == "e":
                print("Bye. Thank you..")
                exit(0)
        else:
            idx = int(main_text)
            agent_id, agent_host, agent_port = find_agent_by_name(agents[idx].get("name",""), agents)
            if agent_id is None:
                print(f"Agent with name '{main_text}' not found. Please try again.")
                continue
            server_address = f"{agent_host}:{agent_port}"
            agent_card = get_agent_card(agent_id, server_address)
            print(f"Connected to agent: {agent_card.name}")


            while True:
                id_base += 1
            
    
                # metadata for the router so that the correct agent is selected.
                metadata.update({ "session_id":session_id, "user_id":user_id})

                logger.info(f"Metadata: {metadata}")

                user_text = input(f"\n\nConnected to: {agent_card.name} Enter your message (e to exit, d to disconnect, g to get agent card): ")
                if user_text == "e":
                    print("Bye. Thank you..")
                    exit(0)
                elif user_text == "d":
                    print("Disconnecting from agent. Restart to connect again.")
                    break
                elif user_text == "g":
                    
                    print(f"Agent Card: {agent_card}")
                    continue
                
                user_message = build_message_request(build_message(str(id_base), Role.ROLE_USER, user_text, metadata=metadata))
                
                
                response = send_message(request=user_message, server_address=server_address)
                logger.info(f">> {response}")
                print(f"Received Response: {response.msg.parts[0].text}") 
        

