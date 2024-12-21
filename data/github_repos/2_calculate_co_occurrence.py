import argparse
import logging

from dotenv import load_dotenv
from neo4j import Driver
from pathlib import Path

from connect_neo4j import connect_neo4j
from setup_logger import setup_logger

logger = setup_logger(__name__)


def load_query(filepath):
    return Path(filepath).read_text()


def execute_query(driver: Driver, query, parameters=None):
    with driver.session() as session:
        result = session.run(query, parameters=parameters)
        return result.consume().counters


def process_co_occurrences(driver: Driver, query_file: str, use_batching: bool, min_occurrence_count: int) -> None:
    """
    Calculate the co-occurrences.

    :param driver: Neo4j driver
    :param query_file: Path to .cypher file containing the query
    :param use_batching: Whether to use the batched version
    :param min_occurrence_count: Minimum number of occurrence for a dependency to be considered
    """
    query = load_query(query_file)
    query_params = {"min_occurrence_count": min_occurrence_count}

    if use_batching:
        # Keep running until no more nodes to process
        while True:
            counters = execute_query(driver, query, query_params)
            if counters.relationships_created == 0:
                break
        logger.info(f"Created {counters.relationships_created} CO_OCCURRENCE relationships")
    else:
        # Run once
        counters = execute_query(driver, query, query_params)
        logger.info(f"Created {counters.relationships_created} CO_OCCURRENCE relationships")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
            Crawl GitHub for JavaScript and TypeScript repositories.
            Use their package.json files to create a dependency graph and store it in a Neo4j database.
            """
    )
    parser.add_argument("--min_occurrence", type=int, help="Minimum number of occurrence for a dependency to be considered.")
    args = parser.parse_args()
    min_occurrence_count = args.min_occurrence if args.min_occurrence else 3

    load_dotenv()
    driver = connect_neo4j()

    use_batching = False
    query_file = "2_co_occurrence_batched.cypher" if use_batching else "2_co_occurrence_simple.cypher"
    process_co_occurrences(driver, query_file, use_batching, min_occurrence_count)

    driver.close()
