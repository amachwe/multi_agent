# TEST
from lib.harness import get_agent_card, send_message
from lib.a2a_grpc_util import build_user_message_response, extract_message_role_and_parts


if __name__ == "__main__":
    server_address = "localhost:50051"
    
    # Get Agent Card
    agent_card = get_agent_card(server_address)
    print("Agent Card:", agent_card)
    

    user_message = build_user_message_response("1", "Hello, Agent!")
    
    response = send_message(_request=user_message, server_address=server_address)
    
    print("Received Response:", response)

