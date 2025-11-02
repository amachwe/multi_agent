# TEST
from lib.harness import get_agent_card, send_message
from lib.a2a_grpc_util import build_message, build_message_request
from a2a_grpc.a2a_pb2 import Role


if __name__ == "__main__":
    server_address = "localhost:50051"
    
    #Get Agent Card
    agent_card = get_agent_card(None,server_address)
    print("Agent Card:", agent_card)
    

    user_message = build_message_request(build_message("1", Role.ROLE_USER,input("Enter your message: ")))
    
    
    response = send_message(request=user_message, server_address=server_address)
    
    print("Received Response:", response)

