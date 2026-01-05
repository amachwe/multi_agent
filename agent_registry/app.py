from flask import Flask, request, jsonify
from typing import Dict
from pydantic import BaseModel


import uuid

CONFIG = {
    "port": 5006,
    "agent_ports" : set([str(i) for i in range(50051,50076)]),
}

app = Flask(__name__)

class AgentRecord(BaseModel):
    id: str
    name: str
    agent_card: dict
    host: str
    port: str

# Sample agent data - In production, this would be a database
agents_db : Dict[str,AgentRecord]  = {}


@app.route('/agent_by_id/<string:agent_id>', methods=['GET'])
def get_agent_by_id_path(agent_id):
    """Get agent by ID via path parameter"""
    agent = agents_db.get(agent_id, None)
    
    if not agent:
        return jsonify({
            "error": "Agent not found",
            "message": f"No agent found with ID: {agent_id}"
        }), 404
    
    return jsonify({
        "success": True,
        "agent": agent
    })

@app.route('/agents', methods=['GET'])
def get_all_agents():
    """Get all agents"""
    return jsonify({
        "success": True,
        "total_agents": len(agents_db),
        "agents": [ agent.model_dump() for agent in agents_db.values() ]
    })

@app.route('/agents/remove/<string:agent_id>', methods=['DELETE'])
def remove_agent(agent_id):
    """Remove agent endpoint"""
    agent = agents_db.pop(agent_id, None)
    
    if not agent:
        return jsonify({
            "error": "Agent not found",
            "message": f"No agent found with ID: {agent_id}"
        }), 404
    
    agent.port and CONFIG["agent_ports"].add(str(agent.port))
    return jsonify({
        "success": True,
        "message": f"Agent with ID: {agent_id} removed successfully"
    })

@app.route('/agents', methods=['POST'])
def add_agent():
    """Add a new agent"""
    data = request.get_json()

    port = str(CONFIG["agent_ports"].pop()) if CONFIG["agent_ports"] else ""
    if port == "":
        return jsonify({
            "error": "Agent port range exceeded",
            "message": "Cannot add more agents, port range exceeded"
        }), 507
    
    required_fields = [ 'name', 'agent_card', 'host']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": "Missing required field",
                "message": f"Field '{field}' is required"
            }), 400
    
    new_agent = AgentRecord(
        id=str(uuid.uuid4()),
        name=data['name'],
        agent_card=data['agent_card'],
        host=data['host'],
        port=f"{port}"
    )
    
    
    agents_db[new_agent.id] = new_agent
    
    return jsonify({
        "success": True,
        "message": "Agent added successfully",
        "agent": new_agent.model_dump(),
        "port": port,
        "host": new_agent.host,
        "id": new_agent.id
    }), 201

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Agent Registry API",
        "port": 5006,
        "total_registered_agents": len(agents_db),
        "available_ports": str(CONFIG["agent_ports"])
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested endpoint does not exist"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

if __name__ == '__main__':
    print("Starting Agent Registry API server...")
    
    
    app.run(host='0.0.0.0', port=CONFIG["port"], debug=False)