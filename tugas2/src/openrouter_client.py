import json
import logging
from typing import Any, Dict, Optional

import requests
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenRouterClient:
    """Client for OpenRouter API"""

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize OpenRouter client

        Args:
            api_key: OpenRouter API key (defaults to Config.OPENROUTER_API_KEY)
            model: Model to use (defaults to Config.OPENROUTER_MODEL)
        """
        self.api_key = api_key or Config.OPENROUTER_API_KEY
        self.model = model or Config.OPENROUTER_MODEL
        self.base_url = Config.OPENROUTER_BASE_URL

        if not self.api_key:
            raise ValueError("OpenRouter API key is required")

    def generate_cypher(
        self, user_query: str, schema_description: str = None
    ) -> Optional[str]:
        """
        Generate Cypher query from natural language

        Args:
            user_query: Natural language query from user
            schema_description: Graph schema description (defaults to Config schema)

        Returns:
            Generated Cypher query string or None if generation fails
        """
        schema = schema_description or Config.get_schema_description()

        system_prompt = f"""You are an expert at converting natural language questions into Neo4j Cypher queries.

{schema}

Important Rules:
1. Generate ONLY valid Cypher query syntax
2. Do NOT include explanations, markdown, or any text except the query
3. Use MATCH patterns for retrieving data
4. Use proper relationship directions
5. ALWAYS use 'code' property for WHERE clause filtering (not 'name')
6. ALWAYS use 'name' property in RETURN clause for display
7. Order results when appropriate
8. Limit results to reasonable numbers (e.g., LIMIT 50)
9. For comparison queries, return data from both entities

Example transformations:
- "coffees from Italy" → MATCH (c:Coffee)-[:ORIGINATES_FROM]->(o:Origin) WHERE o.code = 'italy' RETURN c.name
- "espresso-based coffees" → MATCH (c:Coffee)-[:HAS_BASE]->(b:Base) WHERE b.code = 'espresso' RETURN c.name ORDER BY c.name
- "coffees with no milk" → MATCH (c:Coffee)-[:HAS_MILK]->(m:MilkType) WHERE m.code = 'none' RETURN c.name
- "coffees with steamed milk" → MATCH (c:Coffee)-[:HAS_MILK]->(m:MilkType) WHERE m.code = 'steamed_milk' RETURN c.name, m.name AS milk_type
- "what is espresso" → MATCH (c:Coffee {{code: 'espresso'}}) OPTIONAL MATCH (c)-[r]-(n) RETURN c.name, type(r), labels(n)[0] AS node_type, n.name
- "difference between latte and cappuccino" → MATCH (c:Coffee) WHERE c.code IN ['latte', 'cappuccino'] OPTIONAL MATCH (c)-[r]-(n) RETURN c.name, type(r), labels(n)[0], n.name ORDER BY c.name

Generate ONLY the Cypher query, nothing else."""

        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/coffee-rag-system",
                    "X-Title": "Coffee Knowledge Graph RAG",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_query},
                    ],
                    "temperature": 0.1,  # Low temperature for consistent queries
                    "max_tokens": 500,
                },
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                cypher_query = result["choices"][0]["message"]["content"].strip()

                # Clean up the response - remove markdown code blocks if present
                cypher_query = (
                    cypher_query.replace("```cypher", "").replace("```", "").strip()
                )

                logger.info(f"Generated Cypher query: {cypher_query[:100]}...")
                return cypher_query
            else:
                logger.error("No choices in OpenRouter response")
                return None

        except requests.exceptions.Timeout:
            logger.error("OpenRouter request timed out")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter request failed: {e}")
            return None
        except KeyError as e:
            logger.error(f"Unexpected response format: {e}")
            return None
        except Exception as e:
            logger.error(f"Error generating Cypher: {e}")
            return None

    def chat(self, messages: list, temperature: float = 0.7) -> Optional[str]:
        """
        General chat function for formatting responses

        Args:
            messages: List of message dictionaries with role and content
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            Generated response text
        """
        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": 1000,
                },
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            return None

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return None

    def format_results(self, query: str, results: list) -> str:
        """
        Format query results into natural language

        Args:
            query: Original user query
            results: Query results from Neo4j

        Returns:
            Formatted natural language response
        """
        system_prompt = """You are a helpful assistant that explains coffee knowledge graph query results in natural language.
Convert the technical query results into a friendly, informative response.
Be concise but informative.
If there are multiple results, present them as a numbered list with each item on its own line (e.g., "1. Espresso", "2. Cappuccino").
Do not place multiple list items on the same line.
If there are no results, explain that politely."""

        user_prompt = f"""User asked: "{query}"

Query results (as JSON):
{json.dumps(results, indent=2)}

Please provide a natural language response based on these results."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        return self.chat(messages, temperature=0.3)


if __name__ == "__main__":
    # Test OpenRouter client
    print("Testing OpenRouter Client...")

    try:
        client = OpenRouterClient()

        print("\n1. Testing Cypher generation:")
        test_queries = [
            "What coffees are from Italy?",
            "Show me espresso-based coffees",
            "Which coffees have no milk?",
            "What is the difference between latte and cappuccino?",
        ]

        for query in test_queries:
            print(f"\n   Query: {query}")
            cypher = client.generate_cypher(query)
            if cypher:
                print(f"   Cypher: {cypher}")
            else:
                print("   Failed to generate Cypher")

        print("\nOpenRouter Client test completed")

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("   Please set OPENROUTER_API_KEY in .env file")
