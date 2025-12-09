# Coffee Knowledge Graph - RAG System

## Assignment II - Knowledge Representation and Reasoning (IF4070)

A Retrieval-Augmented Generation (RAG) system for querying coffee knowledge using Neo4j graph database and natural language processing with model from OpenRouter.

---

## Overview

This project implements a knowledge graph based on the coffee domain from Assignment I (Prolog and Ontology) and provides a web-based RAG system for natural language queries.

**Key Features:**
- Neo4j knowledge graph with 11 coffee types
- OpenRouter LLM integration for flexible model selection
- Simple web interface for natural language queries
- Comprehensive testing

---

## Architecture

```
User Query (Natural Language)
        ↓
    Flask Web App
        ↓
   OpenRouter API → Generate Cypher Query
        ↓
    Neo4j Database → Execute Query
        ↓
   Format Results → Natural Language Answer
        ↓
    Display to User
```

### Components:
1. **Neo4j Database** - Knowledge graph storage
2. **Flask Web Application** - User interface
3. **OpenRouter / Gemini Client** - LLM integration (Cypher generation)
4. **RAG Engine** - Orchestrates the query pipeline

---

## Project Structure

```
tugas2/
├── docker-compose.yml          # Neo4j containerization
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
│
├── neo4j/
│   ├── import/
│   │   └── schema.cypher      # Database schema + data
│   └── plugins/               # Exported plugins
│
├── src/
│   ├── app.py                 # Flask application
│   ├── config.py              # Configuration management
│   ├── gemini_client.py       # Gemini API client
│   ├── neo4j_client.py        # Neo4j database client
│   ├── openrouter_client.py   # OpenRouter API client
│   ├── rag_engine.py          # Main RAG logic
│   │
│   ├── static/
│   │   └── style.css          # Web UI styles
│   │
│   └── templates/
│       └── index.html         # Chat interface
│
└── README.md                  # This file
```

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- OpenRouter API key
- Gemini API Key

### 1. Clone and Navigate
```bash
cd Tubes-IF4070-RPP/tugas2
```

### 2. Environment Configuration
```bash
# Copy example environment file
cp .env.example .env
# Edit .env and add your OpenRouter / Gemini API key
```

### 3. Start Neo4j
# run without dump
```bash
# Start Neo4j container
docker-compose up -d

# setup cypher 
docker exec -it neo4j-coffee cypher-shell -u neo4j -p password123 -f /import/setup_coffee_graph.cypher
```

# run with dump
```bash
# setup dump 
docker compose run --rm neo4j neo4j-admin database load neo4j --from-path=/import --overwrite-destination

# Start Neo4j container
docker-compose up -d
```

# to clean data
```bash
# docker condition down first
docker compose run --rm neo4j neo4j-admin database load neo4j --from-path=/import --overwrite-destination
```

### 4. Install Python Dependencies
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 5. Start Flask Application
```bash
cd src
python app.py
```

Access the application at: **http://localhost:8080**

---

## 📊 Knowledge Graph Schema

### Node Types
| Type | Description | Count |
|------|-------------|-------|
| `Coffee` | Coffee beverages | 11 |
| `Base` | Coffee base types | 2 |
| `MilkType` | Milk variations | 6 |
| `Additive` | Extra ingredients | 4 |
| `Preparation` | Brewing methods | 4 |
| `Serving` | Serving styles | 6 |
| `Country` | Countries of origin | 5 |

### Relationship Types
- `HAS_BASE` - Coffee → Base
- `HAS_MILK` - Coffee → MilkType
- `HAS_ADDITIVE` - Coffee → Additive
- `USES_PREPARATION` - Coffee → Preparation
- `SERVED_IN` - Coffee → Serving
- `ORIGINATES_FROM` - Coffee → Country

### Coffee Types (11 total)
1. Espresso
2. Bica
3. Americano
4. Latte
5. Caffè Macchiato
6. Cappuccino
7. Flat White
8. Latte Macchiato
9. Kopi Tubruk
10. Greek Coffee
11. Café Mocha

---

## Development Team

**Kelompok U - IF4070**

| Nama | NIM |
|------|-----|
| Dewantoro Triatmodjo| 13522011 |
| Benardo | 13522055 |
| William Glory henderson | 13522113 |

---