import os
from pathlib import Path

from dotenv import load_dotenv

# Load env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "google").lower()

    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    # Google Gemini Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-flash-latest")
    GOOGLE_EMBEDDING_MODEL = os.getenv(
        "GOOGLE_EMBEDDING_MODEL", "models/text-embedding-004"
    )

    # Neo4j Configuration
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USER = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

    # Flask Configuration
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # Application Settings
    MAX_QUERY_RESULTS = 50
    QUERY_TIMEOUT = 30

    @classmethod
    def validate(cls):
        errors = []

        if cls.MODEL_PROVIDER == "openrouter":
            if not cls.OPENROUTER_API_KEY:
                errors.append("OPENROUTER_API_KEY is not set")
        elif cls.MODEL_PROVIDER == "google":
            if not cls.GOOGLE_API_KEY:
                errors.append("GOOGLE_API_KEY is not set")
        else:
            errors.append(f"Unsupported MODEL_PROVIDER: {cls.MODEL_PROVIDER}")

        if not cls.NEO4J_PASSWORD:
            errors.append("NEO4J_PASSWORD is not set")

        if errors:
            raise ValueError(
                f"Configuration errors:\n" + "\n".join(f"- {e}" for e in errors)
            )

        return True

    @classmethod
    def get_schema_description(cls):
        return """
        Coffee Knowledge Graph Schema:

        IMPORTANT - Property Matching Rules:
        - ALL nodes have two properties: 'code' and 'name'
        - 'code': lowercase identifier for EXACT MATCHING (e.g., "none", "italy", "espresso")
        - 'name': human-readable display name (e.g., "No Milk", "Italy", "Espresso")
        - ALWAYS use 'code' property for WHERE clause filtering
        - ALWAYS use 'name' property for RETURN clause display
        - Example: WHERE m.code = 'none' (correct), NOT WHERE m.name = 'none' (wrong!)

        Node Types:
        - Coffee: Individual coffee beverages
        - Base: Coffee base type
        - MilkType: Type of milk used
        - Additive: Extra ingredients
        - PreparationMethod: Brewing method
        - ServingStyle: Serving style
        - Origin: Country/region of origin

        Relationship Types:
        - HAS_BASE: Coffee -> Base
        - HAS_MILK: Coffee -> MilkType
        - HAS_ADDITIVE: Coffee -> Additive
        - USES_PREPARATION: Coffee -> PreparationMethod
        - SERVED_IN: Coffee -> ServingStyle
        - ORIGINATES_FROM: Coffee -> Origin

        Node Properties (all nodes have these):
        - code (string): Unique lowercase identifier for matching
        - name (string): Display name

        Available Coffee codes:
        espresso, bica, americano, latte, caffe_macchiato, cappuccino,
        flat_white, latte_macchiato, kopi_tubruk, greek_coffee, cafe_mocha

        Available Base codes: espresso, brewed_coffee
        Available MilkType codes: none, steamed_milk, foamed_milk, steamed_and_foamed, microfoam, cold_milk
        Available Additive codes: none, hot_water, sugar, chocolate
        Available PreparationMethod codes: pressure, boiled, diluted, combined
        Available ServingStyle codes: small_cup, tall_glass, large_cup, demitasse, cup, unfiltered
        Available Origin codes: italy, portugal, indonesia, greece, australia_new_zealand
        """


if __name__ == "__main__":
    try:
        Config.validate()
        print("Configuration is valid")
        if Config.MODEL_PROVIDER == "google":
            print(f"Using Gemini model: {Config.GOOGLE_MODEL}")
        else:
            print(f"Using OpenRouter model: {Config.OPENROUTER_MODEL}")
        print(f"Neo4j URI: {Config.NEO4J_URI}")
    except ValueError as e:
        print(f"Configuration error: {e}")
