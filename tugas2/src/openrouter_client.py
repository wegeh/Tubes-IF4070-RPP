import json
import logging
from typing import Any, Dict, Optional

import requests
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenRouterClient:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or Config.OPENROUTER_API_KEY
        self.model = model or Config.OPENROUTER_MODEL
        self.base_url = Config.OPENROUTER_BASE_URL

        if not self.api_key:
            raise ValueError("OpenRouter API key is required")

    def generate_cypher(
        self, user_query: str, schema_description: str = None
    ) -> Optional[str]:
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
10. Never emit a standalone WITH; only use WITH when passing explicit variables to the next clause

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
                    "temperature": 0.1,  
                    "max_tokens": 500,
                },
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                cypher_query = result["choices"][0]["message"]["content"].strip()

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
        system_prompt = """You are a helpful assistant that explains coffee knowledge graph query results in natural language.
Convert the technical query results into a warm, concise response without mentioning any knowledge graph or data source.
If there is exactly one result, describe it in a natural sentence without numbering.
If there are multiple results, give a brief lead-in sentence, then list them as a numbered list with each item on its own line in the exact format:
1. Item
2. Item
3. Item
Each number must be on its own line—no multiple items on one line, no semicolons, and use actual line breaks (or <br> tags) between items.
Complete every sentence; do not leave items hanging. If a value is missing or unknown, explicitly say "not specified".
Leave no extra text after the list.
If there are no results, respond with a polite single sentence stating that no results were found."""

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
