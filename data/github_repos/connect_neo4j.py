import os
from neo4j import GraphDatabase, Driver


def connect_neo4j() -> Driver:
    return GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
    )
