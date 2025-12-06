import os
from pathlib import Path

from dotenv import load_dotenv

# Load env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    # Neo4j Configuration
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "coffeeGraphPassword123")

    # Flask Configuration
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # Application Settings
    MAX_QUERY_RESULTS = 50
    QUERY_TIMEOUT = 30

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []

        if not cls.OPENROUTER_API_KEY:
            errors.append("OPENROUTER_API_KEY is not set")

        if not cls.NEO4J_PASSWORD:
            errors.append("NEO4J_PASSWORD is not set")

        if errors:
            raise ValueError(
                f"Configuration errors:\n" + "\n".join(f"- {e}" for e in errors)
            )

        return True

    @classmethod
    def get_schema_description(cls):
        """Returns schema description for LLM prompting"""
        return """
        Coffee Knowledge Graph Schema:

        Node Types:
        - Coffee: Individual coffee beverages (e.g., espresso, latte)
        - Base: Coffee base type (espresso, brewed_coffee)
        - MilkType: Type of milk used (none, steamed_milk, foamed_milk, microfoam, steamed_and_foamed)
        - Additive: Extra ingredients (none, hot_water, sugar, chocolate)
        - Preparation: Brewing method (pressure, boiled, diluted, combined)
        - Serving: Serving style (small_cup, demitasse, large_cup, tall_glass, cup, unfiltered)
        - Country: Country of origin (italy, portugal, australia_new_zealand, indonesia, greece)

        Relationship Types:
        - HAS_BASE: Coffee -> Base
        - USES_MILK: Coffee -> MilkType
        - CONTAINS: Coffee -> Additive
        - PREPARED_BY: Coffee -> Preparation
        - SERVED_IN: Coffee -> Serving
        - ORIGINATES_FROM: Coffee -> Country
        - SIMILAR_TO: Coffee <-> Coffee (bidirectional similarity)

        Coffee Properties:
        - name (string): Coffee name
        - description (string): Description of the coffee
        - volume_ml (integer): Typical serving volume
        - caffeine_level (string): high, medium, or low

        Available Coffees (11 total):
        espresso, bica, americano, latte, caffe_macchiato, cappuccino,
        flat_white, latte_macchiato, kopi_tubruk, greek_coffee, cafe_mocha
        """


if __name__ == "__main__":
    # Test configuration
    try:
        Config.validate()
        print("Configuration is valid")
        print(f"Using OpenRouter model: {Config.OPENROUTER_MODEL}")
        print(f"Neo4j URI: {Config.NEO4J_URI}")
    except ValueError as e:
        print(f"Configuration error: {e}")
