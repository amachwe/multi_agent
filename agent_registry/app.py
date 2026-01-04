from flask import Flask, request, jsonify
from typing import List
from pydantic import BaseModel


import uuid

app = Flask(__name__)

class AgentRecord(BaseModel):
    id: str
    name: str
    agent_card: dict
    url: str

# Sample agent data - In production, this would be a database
agents_db : List[AgentRecord]  = []

@app.route('/agent_by_id', methods=['GET'])
def get_agent_by_id():
    """Get agent by ID via query parameter"""
    agent_id = request.args.get('id')
    
    if not agent_id:
        return jsonify({
            "error": "Missing required parameter 'id'",
            "message": "Please provide an agent ID as a query parameter"
        }), 400
    
    # Find agent by ID
    agent = next((agent for agent in agents_db if agent['id'] == agent_id), None)
    
    if not agent:
        return jsonify({
            "error": "Agent not found",
            "message": f"No agent found with ID: {agent_id}"
        }), 404
    
    return jsonify({
        "success": True,
        "agent": agent
    })

@app.route('/agent_by_id/<string:agent_id>', methods=['GET'])
def get_agent_by_id_path(agent_id):
    """Get agent by ID via path parameter"""
    agent = next((agent for agent in agents_db if agent['id'] == agent_id), None)
    
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
        "agents": [ agent.model_dump() for agent in agents_db ]
    })

@app.route('/agents', methods=['POST'])
def add_agent():
    """Add a new agent"""
    data = request.get_json()
    
    required_fields = [ 'name', 'agent_card', 'url']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": "Missing required field",
                "message": f"Field '{field}' is required"
            }), 400
    
    if any(agent for agent in agents_db if agent.name == data['name']):
        return jsonify({
            "error": "Agent already exists",
            "message": f"An agent with name '{data['name']}' already exists"
        }), 409
    new_agent = AgentRecord(
        id=str(uuid.uuid4()),
        name=data['name'],
        agent_card=data['agent_card'],
        url=data['url']
    )
    
    agents_db.append(new_agent)
    
    return jsonify({
        "success": True,
        "message": "Agent added successfully",
        "agent": new_agent.model_dump()
    }), 201

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Agent Registry API",
        "port": 5006
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
    
    
    app.run(host='0.0.0.0', port=5006, debug=False)