# TEST
from lib.harness import get_agent_card, send_message
from lib.a2a_grpc_util import build_message, build_message_request
from a2a_grpc.a2a_pb2 import Role
from google.protobuf import struct_pb2

if __name__ == "__main__":
    server_address = "localhost:50051"
    
    #Get Agent Card
    agent_card = get_agent_card(None,server_address)
    print("Agent Card:", agent_card)

    metadata = struct_pb2.Struct()
    agent_directory = ["lg_greeter","adk_greeter"]

    
    while True:
        index = int(input("lg_greeter (1), adk_greeter (2) your selection (0 to exit):"))-1
        if index == -1:
            print("Bye. Thank you..")
            break
        metadata.update({"agent_name": agent_directory[index]})

        print("Metadata:",metadata)

        user_text = input("Enter your message (e to exit): ")
        if user_text == "e":
            print("Bye. Thank you..")
            break
        
        user_message = build_message_request(build_message("1", Role.ROLE_USER, user_text, metadata=metadata))
        
        
        response = send_message(request=user_message, server_address=server_address)
        print(">>", response)
        print("Received Response:", response.msg.parts[0].text) 

