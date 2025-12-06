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
1. Generate ONLY valid Cypher query syntax
2. Do NOT include explanations, markdown, or any text except the query
3. Use MATCH patterns for retrieving data
4. Use proper relationship directions
5. Return relevant properties in the RETURN clause
6. Use WHERE clauses for filtering
7. Order results when appropriate
8. Limit results to reasonable numbers (e.g., LIMIT 50)
9. Handle case-insensitive matching when needed using toLower()
10. For comparison queries, return data from both entities
"""

        prompt = (
            f"{system_prompt}\nUser question: {user_query}\n\n"
            "Return only the Cypher query."
        )

        cypher_query = self._generate_text(prompt, temperature=0.05, max_output_tokens=400)
        if cypher_query:
            return (
                cypher_query.replace("```cypher", "")
                .replace("```", "")
                .strip()
            )
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
Convert the technical query results into a friendly, informative response.
Be concise but informative. If there are multiple results, list them clearly.
If there are no results, explain that politely."""

        user_prompt = f"""User asked: "{query}"

Query results (as JSON):
{json.dumps(results, indent=2)}

Please provide a natural language response based on these results."""

        return self._generate_text(
            f"{system_prompt}\n\n{user_prompt}", temperature=0.3, max_output_tokens=600
        )
