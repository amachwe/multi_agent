# TEST
from lib.harness import get_agent_card, send_message
from lib.a2a_grpc_util import build_message, build_message_request
from a2a_grpc.a2a_pb2 import Role
from google.protobuf import struct_pb2
import random
import argparse

import logging
import os

# Ensure log directory exists
os.makedirs('log', exist_ok=True)

logging.basicConfig(level=logging.INFO, filemode='w', filename='log/harness_client_test.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

AGENT_REGISTRY_URL = os.getenv("AGENT_REGISTRY_URL","http://127.0.0.1:5006")


if __name__ == "__main__":
 
    id_base = 0

    parser = argparse.ArgumentParser(description='A2A Client Test')
    parser.add_argument('--session', type=str, help='Custom session ID', default=str(random.randint(1000,9999)))
    parser.add_argument('--user', type=str, help='Custom user ID', default=str(random.randint(1,100)))
    parser.add_argument('--server', type=str, help='Server address', default="localhost:50051")

    session_id = parser.parse_args().session
    user_id = parser.parse_args().user
    server_address = parser.parse_args().server


    metadata = struct_pb2.Struct()


    while True:
        id_base += 1
      

        # metadata for the router so that the correct agent is selected.
        metadata.update({ "session_id":session_id, "user_id":user_id})

        logger.info(f"Metadata: {metadata}")

        user_text = input("Enter your message (e to exit, g to get agent card): ")
        if user_text == "e":
            print("Bye. Thank you..")
            break
        elif user_text == "g":
            agent_card = get_agent_card(None, server_address)
            print(f"Agent Card: {agent_card}")
            continue
        
        user_message = build_message_request(build_message(str(id_base), Role.ROLE_USER, user_text, metadata=metadata))
        
        
        response = send_message(request=user_message, server_address=server_address)
        logger.info(f">> {response}")
        print(f"Received Response: {response.msg.parts[0].text}") 

