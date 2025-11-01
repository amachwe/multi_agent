from a2a_grpc import a2a_pb2_grpc as a2a_grpc
from a2a_grpc import a2a_pb2 as a2a_proto

def build_message(id:str, role:a2a_proto.Role, message: str) -> a2a_proto.Message:
    message = a2a_proto.Message(
        message_id=id,
        role=role,
        parts = [a2a_proto.Part(text=message)]

    )
    return message

def build_message_response( message: a2a_proto.Message) -> a2a_proto.SendMessageResponse:

    return a2a_proto.SendMessageResponse(msg=message)

def build_message_request(message: a2a_proto.Message) -> a2a_proto.SendMessageRequest:
    return a2a_proto.SendMessageRequest(request=message)

def extract_message_role_and_parts(message: a2a_proto.Message):
    id = message.message_id
    role = message.role
    parts = [part.text for part in message.parts]
    return id, role, parts

