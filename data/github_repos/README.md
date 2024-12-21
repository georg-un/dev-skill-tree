# GitHub repository data

Python project to crawl GitHub for JavaScript and TypeScript repositories and build a dependency graph with the dependency data from the `package.json` files.

## Prerequisites

- Linux
- Docker
- Python >= 3.10
- [virtualenv](https://virtualenv.pypa.io/en/latest/) (for the creation of the Python environment)

## Get started

1. Set up and activate a virtual environment.
   ```bash
   virtualenv env
   source env/bin/activate
   ```
2. Install all required packages.
   ```bash
   python install -r requirements.txt
   ````
3. Create a `.env` file (see [.env.template](./.env.template)).
4. Start a Neo4j docker container.
    ```bash
    NEO4J_PWD=$(grep NEO4J_PASSWORD .env | cut -d= -f2)
    docker run \
        --restart always \
        --publish=7474:7474 --publish=7687:7687 \
        --env NEO4J_AUTH=neo4j/$NEO4J_PWD \
        neo4j
    ```
   
## Usage

1. Crawl GitHub and load the data into Neo4j (this will take very long).
   ```bash
   python3 ./1_crawl_github.py --min_stars=1000
   ```
2. Calculate the co-occurrence on the dependencies.
   ```bash
   python3 ./2_calculate_co_occurrence --min_occurrence=100
   ```
3. You can explore the Neo4j graph visually in the [Neo4j browser](http://localhost:7474/browser/) (URL depends on your configuration).
