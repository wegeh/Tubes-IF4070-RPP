#!/usr/bin/env python3
"""
Neo4j Database Setup Script
Initializes the Neo4j database with coffee knowledge graph schema
"""

import os
import sys
import time

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config
from neo4j_client import Neo4jClient


def wait_for_neo4j(client: Neo4jClient, max_attempts=30):
    """
    Wait for Neo4j to be ready

    Args:
        client: Neo4jClient instance
        max_attempts: Maximum number of connection attempts

    Returns:
        bool: True if Neo4j is ready, False otherwise
    """
    print("Waiting for Neo4j to be ready...")

    for attempt in range(1, max_attempts + 1):
        try:
            if client.connect():
                print("✓ Neo4j is ready!")
                return True
        except Exception as e:
            if attempt == max_attempts:
                print(f"✗ Failed to connect after {max_attempts} attempts")
                return False
            print(f"  Attempt {attempt}/{max_attempts} failed, retrying in 2 seconds...")
            time.sleep(2)

    return False


def clear_database(client: Neo4jClient):
    """
    Clear all data from the database
    
    Args:
        client: Neo4jClient instance
    """
    print("\nClearing existing data...")
    
    try:
        # Delete all nodes and relationships
        client.execute_query("MATCH (n) DETACH DELETE n")
        print("✓ All existing data cleared")
    except Exception as e:
        print(f"✗ Error clearing database: {e}")
        raise


def load_schema_file(filepath: str) -> str:
    """Load Cypher schema from file"""
    with open(filepath, 'r') as f:
        return f.read()


def execute_schema(client: Neo4jClient, schema: str):
    """
    Execute schema creation Cypher statements

    Args:
        client: Neo4jClient instance
        schema: Cypher schema string
    """
    print("\nExecuting schema...")

    # Split by semicolons and execute each statement
    statements = [stmt.strip() for stmt in schema.split(';') if stmt.strip()]

    total = len(statements)
    for i, statement in enumerate(statements, 1):
        # Skip empty statements and comments
        if not statement or statement.startswith('//'):
            continue

        try:
            print(f"  [{i}/{total}] Executing statement ({len(statement)} chars)...")
            client.execute_query(statement)
        except Exception as e:
            print(f"  ✗ Error executing statement {i}: {e}")
            print(f"  Statement: {statement[:100]}...")
            raise

    print(f"✓ Successfully executed {total} statements")


def verify_database(client: Neo4jClient):
    """
    Verify database setup

    Args:
        client: Neo4jClient instance
    """
    print("\nVerifying database setup...")

    # Check node counts
    stats = client.get_database_stats()

    print("\nDatabase Statistics:")
    print("-" * 40)
    for node_type, count in sorted(stats.items()):
        print(f"  {node_type:20s}: {count:3d}")
    print("-" * 40)

    # Verify coffee count
    coffees = client.get_all_coffees()
    expected_coffee_count = 11

    if len(coffees) == expected_coffee_count:
        print(f"✓ Found all {expected_coffee_count} coffee types")
    else:
        print(f"✗ Expected {expected_coffee_count} coffees, found {len(coffees)}")
        return False

    # List all coffees
    print("\nCoffee Types in Database:")
    for coffee in coffees:
        print(f"  - {coffee['name']:20s} ({coffee['description'][:50]}...)")

    # Test a specific coffee
    espresso = client.get_coffee_details('espresso')
    if espresso:
        print("\n✓ Sample query successful (espresso details)")
    else:
        print("\n✗ Failed to retrieve espresso details")
        return False

    print("\n" + "=" * 40)
    print("✓ Database verification complete!")
    print("=" * 40)

    return True


def main():
    """Main setup function"""
    print("=" * 60)
    print("Coffee Knowledge Graph - Database Setup")
    print("=" * 60)

    # Find schema file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    schema_path = os.path.join(project_root, 'neo4j', 'import', 'schema.cypher')

    if not os.path.exists(schema_path):
        print(f"✗ Schema file not found: {schema_path}")
        sys.exit(1)

    print(f"✓ Found schema file: {schema_path}")

    # Load schema
    try:
        schema = load_schema_file(schema_path)
        print(f"✓ Loaded schema ({len(schema)} characters)")
    except Exception as e:
        print(f"✗ Error loading schema: {e}")
        sys.exit(1)

    # Connect to Neo4j
    client = Neo4jClient()

    if not wait_for_neo4j(client):
        print("\n✗ Could not connect to Neo4j")
        print("  Make sure Neo4j is running: docker-compose up -d")
        sys.exit(1)

    try:
        # Clear existing data
        clear_database(client)
        
        # Execute schema
        execute_schema(client, schema)

        # Verify setup
        if verify_database(client):
            print("\n✓ Setup completed successfully!")
            print("\nYou can now start the Flask application:")
            print("  cd src && python app.py")
            return 0
        else:
            print("\n✗ Verification failed")
            return 1

    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main())
