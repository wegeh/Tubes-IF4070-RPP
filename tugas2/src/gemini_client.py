import json
import logging
from typing import Optional

import google.generativeai as genai

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Google Gemini models"""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or Config.GOOGLE_API_KEY
        self.model_name = model or Config.GOOGLE_MODEL

        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is required for Gemini provider")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def _generate_text(
        self, prompt: str, temperature: float = 0.1, max_output_tokens: int = 800
    ) -> Optional[str]:
        """Call Gemini with a simple text prompt"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_output_tokens,
                },
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
        return None

    def generate_cypher(
        self, user_query: str, schema_description: str = None
    ) -> Optional[str]:
        """Generate a Cypher query from natural language"""
        schema = schema_description or Config.get_schema_description()

        system_prompt = f"""You are an expert at converting natural language questions into Neo4j Cypher queries.

{schema}

Important Rules:
1. Generate ONLY valid Cypher query syntax.
2. Do NOT include explanations, markdown, or any text except the query.
3. Use MATCH patterns for retrieving data.
4. Use proper relationship directions.
5. ALWAYS use 'code' property for WHERE clause filtering (not 'name').
6. ALWAYS use 'name' property in RETURN clause for display.
7. Order results when appropriate.
8. Limit results to reasonable numbers (e.g., LIMIT 50).
9. For comparison queries, return data from both entities.
10. Never emit a standalone WITH; only use WITH when passing explicit variables to the next clause.
11. If the user question is outside this coffee schema (e.g., cars, phones, general chat), respond with EXACTLY "OUT_OF_SCOPE" and nothing else.

Example transformations:
- "coffees from Italy" -> MATCH (c:Coffee)-[:ORIGINATES_FROM]->(o:Origin) WHERE o.code = 'italy' RETURN c.name
- "espresso-based coffees" -> MATCH (c:Coffee)-[:HAS_BASE]->(b:Base) WHERE b.code = 'espresso' RETURN c.name ORDER BY c.name
- "coffees with no milk" -> MATCH (c:Coffee)-[:HAS_MILK]->(m:MilkType) WHERE m.code = 'none' RETURN c.name
- "coffees with steamed milk" -> MATCH (c:Coffee)-[:HAS_MILK]->(m:MilkType) WHERE m.code = 'steamed_milk' RETURN c.name, m.name AS milk_type
- "what is espresso" -> MATCH (c:Coffee {{code: 'espresso'}}) OPTIONAL MATCH (c)-[r]-(n) RETURN c.name, type(r), labels(n)[0] AS node_type, n.name
- "difference between latte and cappuccino" -> MATCH (c:Coffee) WHERE c.code IN ['latte', 'cappuccino'] OPTIONAL MATCH (c)-[r]-(n) RETURN c.name, type(r), labels(n)[0], n.name ORDER BY c.name
- "BMW cars on mobile" -> OUT_OF_SCOPE
"""

        prompt = (
            f"{system_prompt}\nUser question: {user_query}\n\n"
            "Return only the Cypher query."
        )

        cypher_query = self._generate_text(prompt, temperature=0.05, max_output_tokens=400)
        if cypher_query:
            cleaned = (
                cypher_query.replace("```cypher", "")
                .replace("```", "")
                .strip()
            )
            return cleaned
        return None

    def chat(self, messages: list, temperature: float = 0.7) -> Optional[str]:
        """Generic chat interface matching OpenRouterClient signature"""
        parts = []
        for message in messages:
            role = message.get("role", "user").upper()
            content = message.get("content", "")
            parts.append(f"{role}: {content}")

        prompt = "\n\n".join(parts)
        return self._generate_text(prompt, temperature=temperature, max_output_tokens=800)

    def format_results(self, query: str, results: list) -> str:
        """Format query results into natural language"""
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

        return self._generate_text(
            f"{system_prompt}\n\n{user_prompt}", temperature=0.3, max_output_tokens=600
        )


if __name__ == "__main__":
    # Test the Gemini client
    print("Testing Gemini Client...")

    try:
        client = GeminiClient()

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

        print("\nGemini Client test completed")

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("   Please set GOOGLE_API_KEY in .env file")
