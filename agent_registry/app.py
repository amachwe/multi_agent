from flask import Flask, request, jsonify
from typing import List, Dict, Optional

app = Flask(__name__)


# Sample agent data - In production, this would be a database
agents_db = [
    {
        "id": "adk_greeter",
        "requires":"ADK",
        "description": "A greeter agent using ADK framework.",
        "skills": ["greeting", "small talk", "user engagement"]
    },
    {
        "id": "lg_greeter",
        "requires":"LangGraph",
        "description": "A greeter agent using LangGraph framework.",
        "skills": ["greeting", "conversation", "user interaction"]
    },
    {
        "id": "dice_roller",
        "requires":"LangGraph",
        "description": "An agent that rolls dice and provides results.",
        "skills": ["random number generation", "dice rolling", "conversation"]
    },
]

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

@app.route('/agent_by_skills', methods=['GET'])
def get_agent_by_skills():
    """Get agents by skills via query parameter"""
    skills_param = request.args.get('skills')
    
    if not skills_param:
        return jsonify({
            "error": "Missing required parameter 'skills'",
            "message": "Please provide skills as a comma-separated query parameter"
        }), 400
    
    # Parse skills (comma-separated)
    requested_skills = [skill.strip().lower() for skill in skills_param.split(',')]
    
    # Find agents that have any of the requested skills
    matching_agents = []
    for agent in agents_db:
        agent_skills_lower = [skill.lower() for skill in agent['skills']]
        if any(skill in agent_skills_lower for skill in requested_skills):
            # Add a match score based on number of matching skills
            matches = len(set(requested_skills) & set(agent_skills_lower))
            agent_with_score = agent.copy()
            agent_with_score['skill_matches'] = matches
            matching_agents.append(agent_with_score)
    
    # Sort by number of matching skills (highest first)
    matching_agents.sort(key=lambda x: x['skill_matches'], reverse=True)
    
    return jsonify({
        "success": True,
        "requested_skills": requested_skills,
        "total_matches": len(matching_agents),
        "agents": matching_agents
    })

@app.route('/agents', methods=['GET'])
def get_all_agents():
    """Get all agents - bonus endpoint"""
    return jsonify({
        "success": True,
        "total_agents": len(agents_db),
        "agents": agents_db
    })

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
    print("Available endpoints:")
    print("  GET /agent_by_id?id=<agent_id>")
    print("  GET /agent_by_id/<agent_id>") 
    print("  GET /agent_by_skills?skills=<skill1,skill2>")
    print("  GET /agents (bonus - get all agents)")
    print("  GET /health (health check)")
    print("\nServer running on http://localhost:5006")
    
    app.run(host='0.0.0.0', port=5006, debug=True)