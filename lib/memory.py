import redis
import argparse
import random

# Simple memory implementation using Redis

r = redis.Redis(host='localhost', port=6379, db=0)

def make_key(client_id: str, session_id: str)-> str:
    return f"{client_id}:{session_id}"

def set_user_memory(client_id: str, session_id: str, memory: str):
    """
    Save user memory to Redis.
    client_id: str - Unique identifier for the client/user.
    session_id: str - Unique identifier for the session.    
    memory: str - Memory content to be saved.
    """
    save_to_memory(client_id, session_id, "user: "+ memory+"\n")

def set_agent_memory(client_id: str, session_id: str, memory: str):
    """
    Save agent memory to Redis.
    client_id: str - Unique identifier for the client/user.
    session_id: str - Unique identifier for the session.    
    memory: str - Memory content to be saved.
    """
    save_to_memory(client_id, session_id, "agent: "+ memory+"\n")

def save_to_memory(client_id: str, session_id: str, memory:str):
    """
    generic save data to memory - not decidng what type of memory entry it is.
    client_id: str - Unique identifier for the client/user.
    session_id: str - Unique identifier for the session.
    memory: str - Memory content to be saved.
    """
    key = make_key(client_id, session_id)
    mem = r.get(key)

    if mem:
        existing_memory = mem.decode('utf-8')
        updated_memory = existing_memory + "\n" + memory
        r.set(key, updated_memory)
    else:
        r.set(key, memory)

def load_from_memory(client_id: str, session_id: str)-> str:
    """
    Load memory from Redis.
    client_id: str - Unique identifier for the client/user.
    session_id: str - Unique identifier for the session.
    Returns the memory content as a string.
    """
    key = make_key(client_id, session_id)
    mem = r.get(key)
    if mem:
        return mem.decode('utf-8')
    return ""


if __name__ == "__main__":
    ## Test the memory function by recalling a memory
    r = redis.Redis(host='localhost', port=6379, db=0)
    parser = argparse.ArgumentParser(description='A2A Client Test')
    parser.add_argument('--session', type=str, help='Custom session ID', default=str(random.randint(1000,9999)))
    parser.add_argument('--user', type=str, help='Custom user ID', default=str(random.randint(1,100)))

    session_id = parser.parse_args().session
    user_id = parser.parse_args().user

    print(load_from_memory(user_id, session_id))
    
