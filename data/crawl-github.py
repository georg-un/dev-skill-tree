import os
import time
import json
import logging
from functools import partial, reduce
from typing import Dict, List, Callable, Any, Optional, Union
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


def parse_package_jsons2(package_jsons: List[ContentFile]) -> Dict[str, Dict[str, str]]:
    """Merge dependencies from multiple package.json files"""

    def extract_deps(package_file: ContentFile) -> Dict[str, Dict[str, str]]:
        try:
            data = json.loads(package_file.decoded_content.decode('utf-8'))
            return {
                'dependencies': data.get('dependencies', {}),
                'devDependencies': data.get('devDependencies', {}),
                'workspaces': data.get('workspaces', [])
            }
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Could not parse {package_file.path}: {e}")
            return {'dependencies': {}, 'devDependencies': {}, 'workspaces': []}

    def merge_deps(
            acc: Dict[str, Dict[str, str]],
            deps: Dict[str, Dict[str, str]]
    ) -> Dict[str, Dict[str, str]]:
        return {
            'dependencies': acc['dependencies'],
            'devDependencies': {**acc['devDependencies'], **deps['devDependencies']},
            'workspaces': list(set(acc.get('workspaces', []) + deps.get('workspaces', [])))
        }

    return reduce(merge_deps, map(extract_deps, package_jsons),
                  {'dependencies': {}, 'devDependencies': {}, 'workspaces': []})


def create_graph_transaction(
        session: Session,
        repo: Repository,
        dependencies: Dict[str, Any]
) -> None:
    """Create Neo4j graph transaction for a repository"""

    def create_repo_node() -> None:
        session.run("""
        MERGE (repo:Repository {name: $name, stars: $stars, url: $url})
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
    add_dependencies('devDependencies', 'DEV_DEPENDENCY')


#def process_repository2(
#        driver: Driver,
#        repo: Repository
#) -> None:
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


def parse_dependencies(package_json: ContentFile, parent_package_jsons: Optional[List[ContentFile]] = None) -> Dict[
    str, Dict[str, str]]:
    """
    Extract dependencies from package.json file.

    If parent package.json files are provided, their devDependencies are merged into the extracted devDependencies.
    """

    if parent_package_jsons is None:
        parent_package_jsons = []

    def extract_deps(package_file: ContentFile) -> Dict[str, Dict[str, str]]:
        try:
            data = json.loads(package_file.decoded_content.decode('utf-8'))
            return {
                'dependencies': data.get('dependencies', {}),
                'peerDependencies': data.get('peerDependencies', {}),
                'devDependencies': data.get('devDependencies', {})
            }
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Could not parse {package_file.path}: {e}")
            return {'dependencies': {}, 'peerDependencies': {}, 'devDependencies': {}}

    def merge_dev_dependencies(
            acc: Dict[str, str],
            curr: Dict[str, str]
    ) -> Dict[str, str]:
        return {**acc, **curr}

    return {
        'dependencies': extract_deps(package_json).get('dependencies', {}),
        'peerDependencies': extract_deps(package_json).get('peerDependencies', {}),
        'devDependencies': reduce(merge_dev_dependencies,
                                  (extract_deps(pkg).get('devDependencies', {}) for pkg in
                                   [package_json] + parent_package_jsons),
                                  {})
    }

def is_parent_of_other_package_json(package_file: ContentFile, other_package_file: ContentFile):
    """Check if one package.json file is a parent of the other package.json file"""
    package_file_data = json.loads(package_file.decoded_content.decode('utf-8'))
    if not package_file_data.get('workspaces'):
        return False

    package_file_path = os.path.dirname(package_file.path)
    other_package_path = os.path.dirname(other_package_file.path)
    for workspace in package_file_data['workspaces']:
        workspace_path = os.path.join(package_file_path, workspace)
        if os.path.commonpath([workspace_path, other_package_path]) == workspace_path:
            return True
    return False

def is_monorepo(package_files: List[ContentFile]) -> bool:
    """Check if any of the package.json files contains the 'workspaces' property"""
    for package_file in package_files:
        try:
            data = json.loads(package_file.decoded_content.decode('utf-8'))
            if 'workspaces' in data:
                return True
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Could not parse {package_file.path}: {e}")
    return False


def process_package_files(package_files: List[ContentFile]):


def process_repository(
        driver: Driver,
        repo: Repository
) -> None:
    """Process a single repository"""
    logger.info(f"Processing {repo.full_name}")

    """
           WHAT WE ACTUALLY NEED TO DO:

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


def crawl_github_ecosystem(
        driver: Driver,
        github_token: str,
        stars_query: str = ">10000",
        max_repos: int = 100_000
) -> None:
    """Crawl GitHub repositories and build ecosystem graph"""
    github = Github(github_token)

    # Search for JavaScript and TypeScript repositories
    query_js = f"stars:{stars_query} language:JavaScript"
    query_ts = f"stars:{stars_query} language:TypeScript"

    try:
        # Paginate through repositories
        for repo in islice(github.search_repositories(query_js), max_repos):
            process_repository(driver, repo)
        for repo in islice(github.search_repositories(query_ts), max_repos):
            process_repository(driver, repo)
    except Exception as e:
        logger.error(f"Error during GitHub ecosystem crawl: {e}")


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
        crawl_github_ecosystem(
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
