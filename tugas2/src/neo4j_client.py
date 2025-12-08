import logging
from typing import Any, Dict, List, Optional

from config import Config
from neo4j import GraphDatabase, exceptions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jClient:
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        self.uri = uri or Config.NEO4J_URI
        self.user = user or Config.NEO4J_USER
        self.password = password or Config.NEO4J_PASSWORD
        self._driver = None

    def connect(self) -> bool:
        try:
            self._driver = GraphDatabase.driver(
                self.uri, auth=(self.user, self.password)
            )
            # Test connection
            self._driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.uri}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            return False

    def close(self):
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed")

    def execute_query(
        self, query: str, parameters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        if not self._driver:
            raise ConnectionError("Not connected to Neo4j. Call connect() first.")

        try:
            with self._driver.session() as session:
                result = session.run(query, parameters or {})
                records = []
                for record in result:
                    record_dict = dict(record)
                    for key, value in record_dict.items():
                        if hasattr(value, "_properties"):
                            record_dict[key] = dict(value._properties)
                        elif hasattr(value, "__iter__") and not isinstance(
                            value, (str, dict)
                        ):
                            record_dict[key] = [
                                (
                                    dict(item._properties)
                                    if hasattr(item, "_properties")
                                    else item
                                )
                                for item in value
                            ]
                    records.append(record_dict)

                logger.info(
                    f"Query executed successfully, returned {len(records)} records"
                )
                return records

        except exceptions.CypherSyntaxError as e:
            logger.error(f"Cypher syntax error: {e}")
            raise ValueError(f"Invalid Cypher query: {e}")
        except exceptions.ClientError as e:
            logger.error(f"Client error: {e}")
            raise
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise

    def validate_query(self, query: str) -> tuple[bool, Optional[str]]:
        try:
            explain_query = f"EXPLAIN {query}"
            with self._driver.session() as session:
                session.run(explain_query)
            return True, None
        except exceptions.CypherSyntaxError as e:
            return False, str(e)
        except Exception as e:
            return False, str(e)

    def get_database_stats(self) -> Dict[str, int]:
        stats_query = """
        MATCH (n)
        WITH labels(n) as labels, count(*) as count
        RETURN labels[0] as type, count
        UNION ALL
        MATCH ()-[r]->()
        WITH type(r) as rel_type, count(*) as count
        RETURN rel_type as type, count
        """
        results = self.execute_query(stats_query)
        return {record["type"]: record["count"] for record in results}

    def get_all_coffees(self) -> List[Dict[str, Any]]:
        query = """
        MATCH (c:Coffee)
        RETURN c.name as name, c.description as description,
               c.volume_ml as volume_ml, c.caffeine_level as caffeine_level
        ORDER BY c.name
        """
        return self.execute_query(query)

    def get_coffee_details(self, coffee_name: str) -> Optional[Dict[str, Any]]:
        query = """
        MATCH (c:Coffee {name: $name})
        OPTIONAL MATCH (c)-[:HAS_BASE]->(base:Base)
        OPTIONAL MATCH (c)-[:USES_MILK]->(milk:MilkType)
        OPTIONAL MATCH (c)-[:CONTAINS]->(additive:Additive)
        OPTIONAL MATCH (c)-[:PREPARED_BY]->(prep:Preparation)
        OPTIONAL MATCH (c)-[:SERVED_IN]->(serving:Serving)
        OPTIONAL MATCH (c)-[:ORIGINATES_FROM]->(country:Country)
        RETURN c, base, milk, additive, prep, serving, country
        """
        results = self.execute_query(query, {"name": coffee_name})
        if results:
            return results[0]
        return None

    def search_coffees(self, criteria: Dict[str, str]) -> List[Dict[str, Any]]:
        conditions = []
        params = {}

        if "base" in criteria:
            conditions.append("(c)-[:HAS_BASE]->(b:Base {name: $base})")
            params["base"] = criteria["base"]

        if "origin" in criteria:
            conditions.append("(c)-[:ORIGINATES_FROM]->(co:Country {name: $origin})")
            params["origin"] = criteria["origin"]

        if "milk" in criteria:
            conditions.append("(c)-[:USES_MILK]->(m:MilkType {name: $milk})")
            params["milk"] = criteria["milk"]

        where_clause = " AND ".join(conditions) if conditions else ""

        query = f"""
        MATCH (c:Coffee)
        {f'WHERE {where_clause}' if where_clause else ''}
        RETURN c.name as name, c.description as description
        ORDER BY c.name
        """

        return self.execute_query(query, params)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    with Neo4jClient() as client:
        print("\n1. Database Statistics:")
        stats = client.get_database_stats()
        for node_type, count in stats.items():
            print(f"   {node_type}: {count}")

        print("\n2. All Coffees:")
        coffees = client.get_all_coffees()
        for coffee in coffees:
            print(f"   - {coffee['name']}: {coffee['description']}")

        print("\n3. Espresso Details:")
        espresso = client.get_coffee_details("espresso")
        if espresso:
            print(f"   {espresso}")

        print("\n4. Search: Coffees from Italy:")
        italian_coffees = client.search_coffees({"origin": "italy"})
        for coffee in italian_coffees:
            print(f"   - {coffee['name']}")

    print("\nNeo4j Client test completed")
