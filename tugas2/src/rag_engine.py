import logging
from typing import Any, Dict, List

from config import Config
from gemini_client import GeminiClient
from neo4j_client import Neo4jClient
from openrouter_client import OpenRouterClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGEngine:
    def __init__(self):
        self.neo4j_client = Neo4jClient()
        self.llm_client = self._init_llm_client()
        self.connected = False

    def _init_llm_client(self):
        provider = Config.MODEL_PROVIDER
        if provider == "google":
            logger.info("Using Google Gemini provider")
            return GeminiClient()
        if provider == "openrouter":
            logger.info("Using OpenRouter provider")
            return OpenRouterClient()
        raise ValueError(f"Unsupported MODEL_PROVIDER: {provider}")

    def connect(self) -> bool:
        self.connected = self.neo4j_client.connect()
        return self.connected

    def disconnect(self):
        self.neo4j_client.close()
        self.connected = False

    def query(self, user_question: str) -> Dict[str, Any]:
        if not self.connected:
            return {
                "question": user_question,
                "cypher": None,
                "results": None,
                "answer": "Error: Not connected to database. Please ensure Neo4j is running.",
                "success": False,
                "error": "Database not connected",
            }

        try:
            logger.info(f"Processing question: {user_question}")
            max_attempts = 3
            cypher_query = None
            validation_error = None
            for attempt in range(1, max_attempts + 1):
                prompt = (
                    user_question
                    if attempt == 1
                    else f"{user_question}\nPrevious Cypher error: {validation_error or 'no query generated'}. Please fix and return only a valid Cypher query."
                )
                cypher_query = self.llm_client.generate_cypher(prompt)
                if not cypher_query:
                    validation_error = "Failed to generate Cypher query"
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts}: no Cypher generated"
                    )
                    continue

                is_valid, validation_error = self.neo4j_client.validate_query(
                    cypher_query
                )
                if is_valid:
                    break

                logger.warning(
                    f"Attempt {attempt}/{max_attempts}: invalid Cypher ({validation_error})"
                )
                cypher_query = None

            if not cypher_query:
                return {
                    "question": user_question,
                    "cypher": None,
                    "results": None,
                    "answer": "I'm not able to answer that right now.",
                    "success": False,
                    "error": f"Invalid Cypher after retries: {validation_error}",
                }

            results = self.neo4j_client.execute_query(cypher_query)

            if not results:
                answer = "I couldn't find any results for your question. The query returned no data."
            else:
                answer = self.llm_client.format_results(user_question, results)
                if not answer:
                    answer = self._format_results_simple(results)

            return {
                "question": user_question,
                "cypher": cypher_query,
                "results": results,
                "answer": answer,
                "success": True,
                "error": None,
            }

        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return {
                "question": user_question,
                "cypher": cypher_query if "cypher_query" in locals() else None,
                "results": None,
                "answer": "I'm not able to answer that right now.",
                "success": False,
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "question": user_question,
                "cypher": cypher_query if "cypher_query" in locals() else None,
                "results": None,
                "answer": "I'm not able to answer that right now.",
                "success": False,
                "error": str(e),
            }

    def _format_results_simple(self, results: List[Dict[str, Any]]) -> str:
        if not results:
            return "No results found."

        if len(results) == 1 and len(results[0]) == 1:
            key = list(results[0].keys())[0]
            return f"Result: {results[0][key]}"

        formatted = []
        for i, record in enumerate(results, 1):
            if len(results) > 1:
                formatted.append(f"{i}. {self._format_record(record)}")
            else:
                formatted.append(self._format_record(record))

        return "\n".join(formatted)

    def _format_record(self, record: Dict[str, Any]) -> str:
        parts = []
        for key, value in record.items():
            if isinstance(value, dict):
                if "name" in value:
                    parts.append(f"{key}: {value['name']}")
                elif "description" in value:
                    parts.append(f"{key}: {value['description']}")
                else:
                    parts.append(f"{key}: {value}")
            elif value is not None:
                parts.append(f"{key}: {value}")

        return ", ".join(parts) if parts else str(record)

    def get_sample_questions(self) -> List[str]:
        return [
            "What coffees are from Italy?",
            "Show me all espresso-based coffees",
            "Which coffees have no milk?",
            "What coffees use steamed milk?",
            "Tell me about espresso",
            "Which coffees are from Indonesia?",
            "What coffees are boiled?",
            "Show me coffees with chocolate",
            "Which coffees are served in a tall glass?",
        ]

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


if __name__ == "__main__":
    try:
        with RAGEngine() as rag:
            test_questions = [
                "What coffees are from Italy?",
                "Tell me about espresso",
                "Which coffees have no milk?",
            ]

            for question in test_questions:
                print(f"\nQ: {question}")
                print("-" * 60)

                result = rag.query(question)

                if result["success"]:
                    print(f"Cypher: {result['cypher']}")
                    print(f"\nResults ({len(result['results'])} records):")
                    for record in result["results"][:3]:  
                        print(f"  {record}")
                    print(f"\nAnswer: {result['answer']}")
                else:
                    print(f"Error: {result['error']}")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Neo4j is running and configured correctly")
