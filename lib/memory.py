import redis
from pydantic import BaseModel



r = redis.Redis(host='localhost', port=6379, db=0)

def make_key(client_id: str, session_id: str)-> str:
    return f"{client_id}:{session_id}"

def set_user_memory(client_id: str, session_id: str, memory: str):
    save_to_memory(client_id, session_id, "user: "+ memory+"\n")

def set_agent_memory(client_id: str, session_id: str, memory: str):
    save_to_memory(client_id, session_id, "agent: "+ memory+"\n")

def save_to_memory(client_id: str, session_id: str, memory:str):
    key = make_key(client_id, session_id)
    mem = r.get(key)

    if mem:
        existing_memory = mem.decode('utf-8')
        updated_memory = existing_memory + "\n" + memory
        r.set(key, updated_memory)
    else:
        r.set(key, memory)

def load_from_memory(client_id: str, session_id: str)-> str:
    key = make_key(client_id, session_id)
    mem = r.get(key)
    if mem:
        return mem.decode('utf-8')
    return ""


if __name__ == "__main__":
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.get