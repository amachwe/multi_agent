import a2a_grpc.a2a_pb2_grpc as a2a_grpc
import a2a_grpc.a2a_pb2 as a2a_proto


def build_agent_message_response(id:str, message: str) -> a2a_proto.Message:
    message = a2a_proto.Message(
        message_id=id,
        role=a2a_proto.Role.ROLE_AGENT,
        parts = [a2a_proto.Part(text=message)]

    )
    return a2a_proto.SendMessageResponse(msg=message)

def build_user_message_response(id:str, message: str) -> a2a_proto.Message:
    message = a2a_proto.Message(
        message_id=id,
        role=a2a_proto.Role.ROLE_USER,
        parts = [a2a_proto.Part(text=message)]

    )
    return a2a_proto.SendMessageResponse(msg=message)