# Agent Registry API Server

A Flask-based REST API server for managing and querying agents by ID and skills.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:5006`

## API Endpoints

### 1. Get Agent by ID

**Method:** GET  
**Endpoints:**
- `/agent_by_id?id=<agent_id>` (query parameter)
- `/agent_by_id/<agent_id>` (path parameter)

**Example:**
```bash
curl "http://localhost:5006/agent_by_id?id=agent_001"
curl "http://localhost:5006/agent_by_id/agent_001"
```

**Response:**
```json
{
  "success": true,
  "agent": {
    "id": "agent_001",
    "name": "Data Analysis Agent",
    "skills": ["data_analysis", "python", "pandas", "visualization"],
    "description": "Specialized in data processing and analysis tasks",
    "status": "active"
  }
}
```

### 2. Get Agents by Skills

**Method:** GET  
**Endpoint:** `/agent_by_skills?skills=<skill1,skill2>`

**Example:**
```bash
curl "http://localhost:5006/agent_by_skills?skills=python,data_analysis"
```

**Response:**
```json
{
  "success": true,
  "requested_skills": ["python", "data_analysis"],
  "total_matches": 2,
  "agents": [
    {
      "id": "agent_001",
      "name": "Data Analysis Agent",
      "skills": ["data_analysis", "python", "pandas", "visualization"],
      "description": "Specialized in data processing and analysis tasks",
      "status": "active",
      "skill_matches": 2
    }
  ]
}
```

### 3. Additional Endpoints

- `GET /agents` - Get all agents
- `GET /health` - Health check

## Sample Data

The server includes 5 sample agents with various skills:
- Data Analysis Agent (data_analysis, python, pandas, visualization)
- Web Scraping Agent (web_scraping, python, selenium, beautifulsoup)  
- NLP Agent (nlp, text_processing, sentiment_analysis, python)
- Database Agent (database, sql, mongodb, data_management)
- API Integration Agent (api_integration, rest, json, python, requests)

## Error Handling

The API returns appropriate HTTP status codes:
- 200: Success
- 400: Bad Request (missing parameters)
- 404: Not Found (agent not found or endpoint not found)
- 500: Internal Server Error