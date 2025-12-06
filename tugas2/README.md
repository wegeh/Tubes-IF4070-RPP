# Coffee Knowledge Graph - RAG System

## Assignment II - Knowledge Representation and Reasoning (IF4070)

A Retrieval-Augmented Generation (RAG) system for querying coffee knowledge using Neo4j graph database and natural language processing with OpenRouter.

---

## 📋 Overview

This project implements a knowledge graph based on the coffee domain from Assignment I (Prolog) and provides a web-based RAG system for natural language queries.

**Key Features:**
- 🗄️ Neo4j knowledge graph with 11 coffee types
- 🤖 OpenRouter LLM integration for flexible model selection
- 🌐 Simple web interface for natural language queries
- 🎯 Focus on query accuracy (>90% target)
- 📊 Comprehensive testing suite

---

## 🏗️ Architecture

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
3. **OpenRouter Client** - LLM integration (Cypher generation)
4. **RAG Engine** - Orchestrates the query pipeline
5. **Testing Suite** - Accuracy validation

---

## 📦 Project Structure

```
tugas2/
├── docker-compose.yml          # Neo4j containerization
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
│
├── neo4j/
│   ├── import/
│   │   └── schema.cypher      # Database schema + data
│   └── backups/               # Exported backups
│
├── src/
│   ├── app.py                 # Flask application
│   ├── config.py              # Configuration management
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
├── scripts/
│   ├── setup_neo4j.py         # Database initialization
│   └── export_backup.sh       # Create Neo4j dump
│
├── tests/
│   └── test_accuracy.py       # Accuracy test suite
│
├── docs/
│   └── laporan.md             # Assignment report
│
└── README.md                  # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- OpenRouter API key ([Get one here](https://openrouter.ai/))

### 1. Clone and Navigate
```bash
cd Tubes-IF4070-RPP/tugas2
```

### 2. Environment Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenRouter API key
nano .env  # or use your preferred editor
```

**Required environment variables:**
```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
NEO4J_PASSWORD=coffeeGraphPassword123
```

### 3. Start Neo4j
```bash
# Start Neo4j container
docker-compose up -d

# Check status
docker-compose ps

# View logs (optional)
docker-compose logs -f
```

### 4. Install Python Dependencies
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 5. Initialize Database
```bash
# Run setup script
python scripts/setup_neo4j.py
```

Expected output:
```
✓ Connected to Neo4j
✓ Successfully executed schema
✓ Found all 11 coffee types
✓ Setup completed successfully!
```

### 6. Start Flask Application
```bash
cd src
python app.py
```

Access the application at: **http://localhost:8080**

---

## 🧪 Testing

### Run Accuracy Tests
```bash
# From project root
python tests/test_accuracy.py
```

This runs 10 test cases covering:
- Geographic queries (coffees from Italy, Indonesia)
- Base ingredient queries (espresso-based, boiled coffees)
- Component queries (milk types, additives)
- Comparison queries (latte vs cappuccino)

**Target Accuracy:** ≥ 90%

### Manual Testing
Use the web interface to test queries like:
- "What coffees are from Italy?"
- "Show me espresso-based coffees"
- "Which coffees have no milk?"
- "What is the difference between latte and cappuccino?"

---

## 📊 Knowledge Graph Schema

### Node Types
| Type | Description | Count |
|------|-------------|-------|
| `Coffee` | Coffee beverages | 11 |
| `Base` | Coffee base types | 2 |
| `MilkType` | Milk variations | 5 |
| `Additive` | Extra ingredients | 4 |
| `Preparation` | Brewing methods | 4 |
| `Serving` | Serving styles | 6 |
| `Country` | Countries of origin | 5 |

### Relationship Types
- `HAS_BASE` - Coffee → Base
- `USES_MILK` - Coffee → MilkType
- `CONTAINS` - Coffee → Additive
- `PREPARED_BY` - Coffee → Preparation
- `SERVED_IN` - Coffee → Serving
- `ORIGINATES_FROM` - Coffee → Country
- `SIMILAR_TO` - Coffee ↔ Coffee

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

## 🔧 Configuration

### OpenRouter Models
You can change the model in `.env`:
```env
# Premium model (higher accuracy)
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Free alternative
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
```

### Neo4j Access
- **Browser UI:** http://localhost:7474
- **Bolt Port:** 7687
- **Username:** neo4j
- **Password:** coffeeGraphPassword123 (from .env)

---

## 📤 Export Database Backup

```bash
# Make script executable
chmod +x scripts/export_backup.sh

# Create backup
./scripts/export_backup.sh
```

Backup will be saved to: `neo4j/backups/coffee_graph_backup_[timestamp].dump`

**Note:** Backup size should be < 5MB for submission.

---

## 🐛 Troubleshooting

### Neo4j won't start
```bash
# Check Docker logs
docker-compose logs neo4j

# Restart container
docker-compose restart neo4j
```

### Connection errors
```bash
# Verify Neo4j is running
docker-compose ps

# Test connection
docker exec coffee-knowledge-graph cypher-shell -u neo4j -p coffeeGraphPassword123 "RETURN 1"
```

### Flask errors
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check environment variables
python src/config.py
```

### OpenRouter API errors
- Verify API key is correct in `.env`
- Check API key has credits/quota
- Try a free model first: `meta-llama/llama-3.1-8b-instruct:free`

---

## 📚 Sample Queries

Try these natural language questions:

**Geography:**
- "What coffees are from Italy?"
- "Show me coffee from Indonesia"

**Ingredients:**
- "Which coffees have no milk?"
- "What coffees use steamed milk?"
- "Show me coffees with chocolate"

**Preparation:**
- "Which coffees are boiled?"
- "What are espresso-based coffees?"

**Comparison:**
- "What is the difference between latte and cappuccino?"
- "Compare espresso and americano"

**Details:**
- "Tell me about espresso"
- "What is kopi tubruk?"

---

## 🎯 Assignment Requirements Checklist

- ✅ **Knowledge Graph:** 11 coffees with properties and relationships
- ✅ **Neo4j Schema:** Complete graph structure matching Prolog domain
- ✅ **Data Population:** All coffee data from Assignment I
- ✅ **RAG System:** OpenRouter + Neo4j integration
- ✅ **Natural Language Interface:** Flask web application
- ✅ **Query Accuracy:** Testing suite with >90% target
- ✅ **Neo4j Backup:** Export script and dump file (< 5MB)
- ✅ **Documentation:** README and report framework

---

## 📝 Development Team

**Kelompok U - IF4070**

[Add your team member names and contributions here]

---

## 📖 References

- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [text2cypher Dataset](https://huggingface.co/datasets/neo4j/text2cypher-2025v1)

---

## 📄 License

This project is developed for academic purposes as part of IF4070 coursework.

---

**For detailed implementation report, see:** [`docs/laporan.md`](docs/laporan.md)
