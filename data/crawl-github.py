import os
import time
import json
import logging
from functools import partial, reduce
from typing import Dict, List, Callable, Any, Optional, Union, Tuple
from itertools import islice

import requests
from github import Github, GithubException
from github.Repository import Repository
from github.ContentFile import ContentFile
from neo4j import GraphDatabase, Driver, Session
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def retry_with_backoff(
        func: Callable[..., Any],
        *args: Any,
        max_retries: int = 5,
        base_delay: int = 2
) -> Any:
    """Functional retry mechanism with exponential backoff"""

    # TODO: If rate limited, wait
    def attempt(attempt_num: int) -> Any:
        try:
            return func(*args)
        except Exception as e:
            if attempt_num >= max_retries:
                logger.error(f"Operation failed after {max_retries} attempts: {e}")
                raise
            delay = base_delay * (2 ** attempt_num)
            logger.warning(f"Retry {attempt_num + 1} failed. Retrying in {delay} seconds. Error: {e}")
            time.sleep(delay)
            return attempt(attempt_num + 1)

    return attempt(0)


def find_package_jsons(
        repo: Repository,
        max_depth: int = 3,
) -> List[ContentFile]:
    """Recursively find package.json files in a repository"""

    def search_contents(
            contents: List[ContentFile],
            current_depth: int = 0
    ) -> List[ContentFile]:
        if current_depth > max_depth:
            return []

        found_packages = []
        for content in contents:
            try:
                if content.type == 'dir':
                    # Recursively search directories
                    dir_contents = retry_with_backoff(repo.get_contents, content.path)
                    found_packages.extend(
                        search_contents(dir_contents, current_depth + 1)
                    )
                elif content.name == 'package.json':
                    found_packages.append(content)
            except GithubException as e:
                logger.warning(f"Error processing {content.path}: {e}")

        return found_packages

    try:
        root_contents = retry_with_backoff(repo.get_contents, "/")
        return search_contents(root_contents)
    except Exception as e:
        logger.error(f"Could not find package.json in {repo.full_name}: {e}")
        return []


def parse_package_file(package_file: ContentFile, root_package_file: Optional[ContentFile]) -> Dict[str, Dict[str, str]]:
    """
    Take a package file and, optionally, its root package file and parse the dependencies.
    If a root package file is provided, the devDependencies of both files are merged in the final output.

    :param package_file:        The package file to process
    :param root_package_file:   A root package file that can be provided in the case of a monorepo
    :return:                    A dictionary of dependencies and metadata, e.g. { dependencies: { lodash: 1.3.0 } }
    """
    def extract_deps(file: ContentFile) -> Dict[str, Dict[str, str]]:
        try:
            data = json.loads(file.decoded_content.decode('utf-8'))
            return {
                'dependencies': data.get('dependencies', {}),
                'peerDependencies': data.get('peerDependencies', {}),
                'devDependencies': data.get('devDependencies', {}),
            }
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Could not parse {file.path}: {e}")
            return {'dependencies': {}, 'peerDependencies': {}, 'devDependencies': []}

    parsed_file = extract_deps(package_file)

    if root_package_file:
        parsed_root_file = extract_deps(root_package_file)
        parsed_file['devDependencies'] = {**parsed_root_file.get('devDependencies'), **parsed_file.get('devDependencies')}

    return parsed_file


def store_in_database(
        session: Session,
        repo: Repository,
        dependencies: Dict[str, Any]
) -> None:
    """Create Neo4j graph transaction for a repository"""

    """
        NOTES
        - Including the versions of repos or dependencies blows up complexity. Ignore them for now.
        - Workflow:
            - Create/update repo node.
            - For each dep, create a node if it doesn't exist yet.
            - Create edges between nodes.
    """

    def upsert_repo_node() -> None:
        session.run("""
        MERGE (package:Package {name: $name, stars: $stars, url: $url})
        """, {
            'name': repo.full_name,
            'stars': repo.stargazers_count,
            'url': repo.html_url,
        })

    def add_dependencies(dep_type: str, relationship: str) -> None:
        for package_name, version in dependencies[dep_type].items():
            session.run(f"""
            MERGE (pkg:Package {{name: $package_name}})
            MERGE (repo)-[:{relationship} {{version: $version}}]->(pkg)
            """, {
                'package_name': package_name,
                'version': version
            })

    create_repo_node()
    add_dependencies('dependencies', 'PROD_DEPENDENCY')
    add_dependencies('peerDependencies', 'PEER_DEPENDENCY')
    add_dependencies('devDependencies', 'DEV_DEPENDENCY')


# def process_repository2(
#        driver: Driver,
#        repo: Repository
# ) -> None:
#    """Process a single repository"""
#    logger.info(f"Processing {repo.full_name}")
#
#    try:
#       # Find package.json files
#       package_jsons = find_package_jsons(repo)
#
#        if not package_jsons:
#            logger.info(f"No package.json found in {repo.full_name}")
#            return
#
#        # Extract and merge dependencies
#        dependencies = parse_package_jsons(package_jsons)
#
#        # Create graph transaction
#        with driver.session() as session:
#            create_graph_transaction(session, repo, dependencies)
#
#        logger.info(f"Processed {repo.full_name} successfully")
#
#    except Exception as e:
#        logger.error(f"Failed to process {repo.full_name}: {e}")


def find_root_package_file(package_files: List[ContentFile]) -> Optional[ContentFile]:
    """Find the root package.json file if there is one."""
    for package_file in package_files:
        try:
            data = json.loads(package_file.decoded_content.decode('utf-8'))
            if 'workspaces' in data:
                return package_file
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Could not parse {package_file.path}: {e}")
        return None


def extract_root_package_file(package_files: List[ContentFile]) -> Tuple[List[ContentFile], Optional[ContentFile]]:
    """
        Take a list of all package files and extract the root package file from it.
        Return a tuple containing all non-root package files and, if found, the root package file.
    """
    root_package_file = find_root_package_file(package_files)
    if root_package_file:
        return [file for file in package_files if file != root_package_file], root_package_file
    return package_files, None


def process_package_files(package_files: List[ContentFile]):
    [non_root_package_files, root_package_file] = extract_root_package_file(package_files)

def process_repository(
        driver: Driver,
        repo: Repository
) -> None:
    """Process a single repository"""
    logger.info(f"Processing {repo.full_name}")

    """
           TODO: WHAT WE ACTUALLY NEED TO DO:

           If we only find one package.json --> use that one
           If we find multiple package.json:
               Check if they have a workspaces property.
               If one has a workspace prop and references the folder of the other, that's the root
               If none of them has a workspace prop, they're siblings

               If there is no hierarchy --> process them sequentially individually
               If there is a hierarchy, process them recursively

           Processing of flat package.json files:
               Return dependencies, devDependencies, peerDependencies, and metadata

           Processing of monorepo package.json files:
                First, get all package.json files. Children, grandchildren, ...
                Merge them sequentially.


           Notes:

           Pay attention to file references (e.g. "myDep": "file: ../...")!
           monitor how many repos have a parent.repo. That tells you if you should include sub-repos.
           
           I think we should store the repository information on the package node. 
           In the case of a monorepo, we store it multiple times but most repos are probably not monorepos anyways.

           Also relevant (for security analysis):
           repo.get_contributors().totalCount
           repo.last_modified             
           """

    try:
        # Find package.json files
        package_jsons = find_package_jsons(repo)

        if not package_jsons:
            logger.info(f"No package.json found in {repo.full_name}")
            return

        [print(file.path) for file in package_jsons]

        if len(package_jsons) != 1:
            return

        # Extract and merge dependencies
        dependencies = parse_dependencies(package_jsons[0])
        print(dependencies)

        # Create graph transaction
        # with driver.session() as session:
        #    create_graph_transaction(session, repo, dependencies)
        # print(dependencies)

        logger.info(f"Processed {repo.full_name} successfully")

    except Exception as e:
        logger.error(f"Failed to process {repo.full_name}: {e}")


def crawl_github(
        driver: Driver,
        github_token: str,
        stars_query: str = ">10000",
        max_repos: int = 100_000
) -> None:
    """Crawl GitHub repositories and build ecosystem graph"""
    github = Github(github_token)

    query_js = f"stars:{stars_query} language:JavaScript"
    query_ts = f"stars:{stars_query} language:TypeScript"

    try:
        # Paginate through repositories
        for repo in islice(github.search_repositories(query_js), max_repos): # JavaScript
            process_repository(driver, repo)
        for repo in islice(github.search_repositories(query_ts), max_repos): # TypeScript
            process_repository(driver, repo)
    except Exception as e:
        logger.error(f"Error while crawling GitHub: {e}")


def main() -> None:
    """Main entry point for the crawler"""
    load_dotenv()

    # Create Neo4j driver
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
    )

    try:
        # Crawl GitHub ecosystem
        crawl_github(
            driver,
            os.getenv('GITHUB_TOKEN'),
            stars_query="1234",
            max_repos=100_000
        )
    except Exception as e:
        logger.error(f"Crawler failed: {e}")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
