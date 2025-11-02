from a2a_grpc import a2a_pb2_grpc as a2a_grpc
from a2a_grpc import a2a_pb2 as a2a_proto
from a2a_grpc.a2a_pb2 import Role
from google.genai.types import Content, Part

def map_code_to_role(role: Role) -> str:
    if role == Role.ROLE_AGENT:
            role_name = "model"
    elif role == Role.ROLE_USER:
            role_name = "user"
    elif role == Role.ROLE_UNSPECIFIED:
            role_name = ""

def map_message_to_agent_content(message: a2a_proto.Message) -> Content:
    parts = [Part(text=part.text) for part in message.parts]
    role = map_code_to_role(message.role)

    return Content(role=role,parts=parts)

def build_message(id:str, role:a2a_proto.Role, message: str) -> a2a_proto.Message:
    message = a2a_proto.Message(
        message_id=id,
        role=role,
        parts = [a2a_proto.Part(text=message)]

    )
    return message

def build_message_from_parts(id:str, role:a2a_proto.Role, parts: list[a2a_proto.Part]) -> a2a_proto.Message:
    message = a2a_proto.Message(
        message_id=id,
        role=role,
        parts = parts
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

