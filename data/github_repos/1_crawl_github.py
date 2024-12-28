import argparse
import json
import os
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from github import GithubException
from github.ContentFile import ContentFile
from github.Repository import Repository
from neo4j import Driver, Session

from connect_neo4j import connect_neo4j
from repository_search import RepositorySearch
from setup_logger import setup_logger

logger = setup_logger(__name__)


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
                    dir_contents = repo.get_contents(content.path)
                    found_packages.extend(
                        search_contents(dir_contents, current_depth + 1)
                    )
                elif content.name == 'package.json':
                    found_packages.append(content)
            except GithubException as e:
                logger.warning(f"Error processing {content.path}: {e}")

        return found_packages

    try:
        root_contents = repo.get_contents("/")
        return search_contents(root_contents)
    except Exception as e:
        logger.error(f"Could not find package.json in {repo.full_name}: {e}")
        return []


def parse_package_file_dependencies(package_file: ContentFile, root_package_file: Optional[ContentFile]) -> Dict[
    str, Dict[str, str]]:
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
        parsed_file['devDependencies'] = {**parsed_root_file.get('devDependencies'),
                                          **parsed_file.get('devDependencies')}

    return parsed_file


def store_in_database(
        session: Session,
        repo: Repository,
        dependencies: Dict[str, Dict[str, str]]
) -> None:
    """Create Neo4j graph transaction for a repository"""

    """
        NOTES
        - Including the versions of repos or dependencies blows up complexity. Ignore them for now.
        - Workflow in neo4j:
            - Create/update repo node.
            - For each dep, create a node if it doesn't exist yet.
            - Create edges between nodes.
    """

    def upsert_repo_node(repo: Repository) -> None:
        """Upsert the repo information (stars, url, ...) of a package in the database"""
        session.run("""
        MERGE (package:Package {
            name: $name,
            stars: $stars,
            watchers: $watchers,
            open_issues: $open_issues,
            contributors: $contributors,
            last_modified: datetime($last_modified),
            url: $url
        })
        """, {
            'name': repo.full_name,
            'stars': repo.stargazers_count,
            'watchers': repo.watchers_count,
            'open_issues': repo.open_issues_count,
            'contributors': repo.get_contributors().totalCount,
            'last_modified': repo.updated_at.isoformat(),
            'url': repo.html_url,
        })

    def upsert_dependency_node(dependency: str) -> None:
        """Insert a dependency as package node if it doesn't exist yet."""
        session.run("""
        MERGE (package:Package {name: $name})
        """, {
            'name': dependency
        })

    def insert_dependency_edge(repo_name: str, dependency: str, relationship: str) -> None:
        """Insert a dependency edge from one package to the other"""
        session.run(f"""
        MATCH (repo:Package {{name: $repo_name}})
        MATCH (pkg:Package {{name: $dependency}})
        MERGE (repo)-[:{relationship}]->(pkg)
        """, {
            'repo_name': repo_name,
            'dependency': dependency
        })

    def get_edge_name(dependency_type: str) -> str:
        match dependency_type:
            case 'dependencies':
                return 'PROD_DEPENDENCY'
            case 'peerDependencies':
                return 'PEER_DEPENDENCY'
            case 'devDependencies':
                return 'DEV_DEPENDENCY'

    upsert_repo_node(repo)

    for dependency_type in dependencies:
        for dependency_name in dependencies.get(dependency_type):
            upsert_dependency_node(dependency_name)
            edge_name = get_edge_name(dependency_type)
            insert_dependency_edge(repo.full_name, dependency_name, edge_name)


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


def process_package_files(session: Session, repo: Repository, package_files: List[ContentFile]):
    [non_root_package_files, root_package_file] = extract_root_package_file(package_files)

    for non_root_package_file in non_root_package_files:
        dependencies = parse_package_file_dependencies(non_root_package_file, root_package_file)
        store_in_database(session, repo, dependencies)


def process_repository(
        driver: Driver,
        repo: Repository
) -> None:
    """Process a single repository"""
    logger.info(f"Processing {repo.full_name}")

    """
       Notes:

       Pay attention to file references (e.g. "myDep": "file: ../...")!
       monitor how many repos have a parent.repo. That tells you if you should include sub-repos.
       
       I think we should store the repository information on the package node. 
       In the case of a monorepo, we store it multiple times but most repos are probably not monorepos anyways.
   """

    try:
        package_jsons = find_package_jsons(repo)

        if not package_jsons:
            logger.info(f"No package.json found in {repo.full_name}")
            return

        with driver.session() as session:
            process_package_files(session, repo, package_jsons)

        logger.info(f"Processed {repo.full_name} successfully")

    except Exception as e:
        logger.error(f"Failed to process {repo.full_name}: {e}")


def crawl_github(
        driver: Driver,
        github_token: str,
        min_stars: int,
) -> None:
    """Crawl GitHub repositories and build ecosystem graph"""
    try:
        js_repo_search = RepositorySearch(github_token, min_stars, "JavaScript")
        for repo in js_repo_search.query():
            process_repository(driver, repo)

        ts_repo_search = RepositorySearch(github_token, min_stars, "TypeScript")
        for repo in ts_repo_search.query():
            process_repository(driver, repo)

    except Exception as e:
        logger.error(f"Error while crawling GitHub: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Crawl GitHub for JavaScript and TypeScript repositories.
        Use their package.json files to create a dependency graph and store it in a Neo4j database.
        """
    )
    parser.add_argument("--min_stars", type=int, required=True, help="Minimum number of stars a repo needs to have.")
    args = parser.parse_args()

    load_dotenv()
    driver = connect_neo4j()
    github_token = os.getenv('GITHUB_TOKEN')

    try:
        crawl_github(driver, github_token, args.min_stars)
    except Exception as e:
        logger.error(f"Crawler failed: {e}")
    finally:
        driver.close()
