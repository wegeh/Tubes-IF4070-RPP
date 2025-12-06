"""
Flask Web Application for Coffee Knowledge Graph RAG System
Provides a simple chat interface for querying the coffee knowledge graph
"""

import atexit
from pathlib import Path

from dotenv import load_dotenv

# Load env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

import logging
import traceback
from datetime import datetime

from config import Config
from flask import Flask, jsonify, render_template, request, session
from rag_engine import RAGEngine

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY
app.config["DEBUG"] = Config.FLASK_DEBUG

# Initialize RAG engine
rag_engine = None


def get_rag_engine():
    """Get or create RAG engine instance"""
    global rag_engine
    if rag_engine is None:
        rag_engine = RAGEngine()
        rag_engine.connect()
    return rag_engine


@app.route("/")
def index():
    """Render main chat interface"""
    # Initialize session history if not exists
    if "history" not in session:
        session["history"] = []

    # Get sample questions
    try:
        rag = get_rag_engine()
        sample_questions = rag.get_sample_questions()
    except Exception as e:
        logger.error(f"Error getting sample questions: {e}")
        sample_questions = [
            "What coffees are from Italy?",
            "Tell me about espresso",
            "Which coffees have no milk?",
        ]

    return render_template("index.html", sample_questions=sample_questions)


@app.route("/query", methods=["POST"])
def query():
    """
    Handle user query

    Expected JSON:
        {
            "question": "user's question"
        }

    Returns JSON:
        {
            "success": true/false,
            "question": "original question",
            "cypher": "generated Cypher query",
            "results": [...],
            "answer": "natural language answer",
            "error": "error message if any",
            "timestamp": "query timestamp"
        }
    """
    try:
        data = request.get_json()
        user_question = data.get("question", "").strip()

        if not user_question:
            return (
                jsonify({"success": False, "error": "Please provide a question"}),
                400,
            )

        # Get RAG engine
        rag = get_rag_engine()

        # Process query
        result = rag.query(user_question)

        # Add timestamp
        result["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Store in session history
        if "history" not in session:
            session["history"] = []

        session["history"].append(
            {
                "question": user_question,
                "answer": result["answer"],
                "timestamp": result["timestamp"],
            }
        )

        # Keep only last 20 queries
        if len(session["history"]) > 20:
            session["history"] = session["history"][-20:]

        session.modified = True

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        logger.error(traceback.format_exc())
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Server error: {str(e)}",
                    "question": data.get("question", "") if "data" in locals() else "",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            ),
            500,
        )


@app.route("/history")
def history():
    """Get query history"""
    return jsonify({"history": session.get("history", [])})


@app.route("/clear-history", methods=["POST"])
def clear_history():
    """Clear query history"""
    session["history"] = []
    session.modified = True
    return jsonify({"success": True})


@app.route("/health")
def health():
    """Health check endpoint"""
    try:
        rag = get_rag_engine()
        db_connected = rag.connected

        return jsonify(
            {
                "status": "healthy" if db_connected else "degraded",
                "database_connected": db_connected,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            503,
        )


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


def cleanup_on_exit():
    """Cleanup when process exits"""
    global rag_engine
    if rag_engine is not None:
        try:
            rag_engine.disconnect()
            logger.info("RAG engine disconnected")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Register cleanup to run on process exit
atexit.register(cleanup_on_exit)


if __name__ == "__main__":
    print(f"Starting Flask app in {Config.FLASK_ENV} mode")
    print(f"Model provider: {Config.MODEL_PROVIDER}")
    if Config.MODEL_PROVIDER == "google":
        print(f"Using Gemini model: {Config.GOOGLE_MODEL}")
    else:
        print(f"Using OpenRouter model: {Config.OPENROUTER_MODEL}")
    print(f"Neo4j URI: {Config.NEO4J_URI}")

    # Initialize application
    try:
        # Validate configuration
        Config.validate()
        logger.info("Configuration loaded")

        # Initialize RAG engine
        rag = get_rag_engine()
        logger.info("RAG engine initialized")

    except Exception as e:
        logger.error(f"Initialization error: {e}")

    print("\nAccess the application at: http://localhost:8080")
    print("\nPress CTRL+C to stop the server")

    app.run(host="0.0.0.0", port=8080, debug=Config.FLASK_DEBUG)
