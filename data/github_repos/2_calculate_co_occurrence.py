import logging

from dotenv import load_dotenv
from neo4j import Driver
from pathlib import Path

from connect_neo4j import connect_neo4j
from github_repos.setup_logger import setup_logger

logger = setup_logger(__name__)


def load_query(filepath):
    return Path(filepath).read_text()


def execute_query(driver: Driver, query):
    with driver.session() as session:
        result = session.run(query)
        return result.consume().counters


def process_co_occurrences(driver: Driver, query_file: str, use_batching: bool) -> None:
    """
    Calculate the co-occurrences.

    :param driver: Neo4j driver
    :param query_file: Path to .cypher file containing the query
    :param use_batching: Whether to use the batched version
    """
    query = load_query(query_file)

    if use_batching:
        # Keep running until no more nodes to process
        while True:
            counters = execute_query(driver, query)
            if counters.relationships_created == 0:
                break
        logger.info(f"Created {counters.relationships_created} CO_OCCURRENCE relationships")
    else:
        # Run once
        counters = execute_query(driver, query)
        logger.info(f"Created {counters.relationships_created} CO_OCCURRENCE relationships")


if __name__ == "__main__":
    load_dotenv()
    driver = connect_neo4j()

    use_batching = True
    query_file = "2_co_occurrence_batched.cypher" if use_batching else "2_co_occurrence_simple.cypher"
    process_co_occurrences(driver, query_file, use_batching)

    driver.close()
