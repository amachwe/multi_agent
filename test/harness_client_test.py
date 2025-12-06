# TEST
from lib.harness import get_agent_card, send_message
from lib.a2a_grpc_util import build_message, build_message_request
from a2a_grpc.a2a_pb2 import Role
from google.protobuf import struct_pb2
import random
import argparse

import logging

logging.basicConfig(level=logging.INFO, filemode='w', filename='harness_client_test.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    server_address = "localhost:50051"
    id_base = 0

    parser = argparse.ArgumentParser(description='A2A Client Test')
    parser.add_argument('--session', type=str, help='Custom session ID', default=str(random.randint(1000,9999)))
    parser.add_argument('--user', type=str, help='Custom user ID', default=str(random.randint(1,100)))

    session_id = parser.parse_args().session
    user_id = parser.parse_args().user

    #Get Agent Card
    agent_card = get_agent_card(None,server_address)
    logger.info(f"Agent Card: {agent_card}")

    metadata = struct_pb2.Struct()
    agent_registry = ["lg_greeter","adk_greeter"]

    
    while True:
        id_base += 1
        index = int(input("lg_greeter (1), adk_greeter (2) your selection (0 to exit):"))-1
        if index == -1:
            print("Bye. Thank you..")
            break

        # metadata for the router so that the correct agent is selected.
        metadata.update({"agent_name": agent_registry[index], "session_id":session_id, "user_id":user_id})

        logger.info(f"Metadata: {metadata}")

        user_text = input("Enter your message (e to exit): ")
        if user_text == "e":
            print("Bye. Thank you..")
            break
        
        user_message = build_message_request(build_message(str(id_base), Role.ROLE_USER, user_text, metadata=metadata))
        
        
        response = send_message(request=user_message, server_address=server_address)
        logger.info(f">> {response}")
        print(f"Received Response: {response.msg.parts[0].text}") 

