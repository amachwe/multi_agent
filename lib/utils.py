import requests
import json
import os
import logging
from google.protobuf import struct_pb2
from lib.harness import send_message
from lib.a2a_grpc_util import build_message, build_message_request
from a2a_grpc.a2a_pb2 import Role

os.makedirs('log', exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, filemode='w', filename='log/agent_runner_server.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

AGENT_REGISTRY_URL = os.getenv("AGENT_REGISTRY_URL","http://127.0.0.1:5006")

def get_all_agents()->dict:
    response = requests.get(f"{AGENT_REGISTRY_URL}/agents")
    if response.status_code == 200:
        data = response.json()
        return data.get("agents",{})
    else:
        logger.error(f"Failed to get agents: {response.status_code} - {response.text}")
        return {}
    
if __name__ == "__main__":
    agents = get_all_agents()
    logger.info(f"Registered agents: {agents}")
    print(f"Registered agents: {agents}")


def build_instructions_for_agents():
    all_agents = []


    try:
        all_agents = get_all_agents()
        
        if all_agents:
            agent_dict = {}
            logger.info(f"Agents available: {all_agents}")
            agent_instr = ""
            for agent in all_agents:
                
                name = agent['agent_card']['name']
                agent_dict[name] = agent
                description = agent['agent_card'].get('description','No description available')
                skills = agent['agent_card'].get('skills',[])

                skills_instr = ""
                for skill in skills:
                    skills_instr += str(skill)+"\n"


                agent_instr += f"Agent Name: {name}; Description: {description}; Skills: {skills_instr}\n"
                
            
            return f"""
            You can also contact other agents to get information:
            {agent_instr}\n

            """, agent_dict
    except Exception as e:
        logger.error(f"Error getting all agents: {e}")
    
        return "", {}
    

if __name__ == "__main__": 
    instructions, _ = build_instructions_for_agents()
    print(instructions)
