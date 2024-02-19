from typing import TypedDict, List

import requests
import psycopg

from config import POSTGRES_CONFIG


# StackExchange API parameters
API_URL = "https://api.stackexchange.com/2.3/tags/synonyms"
SITE = "stackoverflow"


class TagSynonymMapping(TypedDict):
    creation_date: int
    last_applied_date: int
    applied_count: int
    to_tag: str
    from_tag: str


def fetch_all_tag_synonyms() -> List[TagSynonymMapping]:
    """
    Fetch all tag synonyms from StackExchange API.
    :return:        A list of tag synonym mappings.
    """
    print("Fetching all synonyms from StackExchange API", end="")
    synonyms = []
    page = 1
    has_more = True
    while has_more:
        if page % 1 == 0:
            print(".", end="")
        response = requests.get(API_URL, params={
            'site': SITE,
            'page': page,
            'pagesize': 100  # Adjust based on what the API supports
        })
        if response.status_code == 200:
            data = response.json()
            synonyms.extend(data['items'])
            has_more = data.get('has_more', False)
            page += 1
        else:
            break  # Exit if there's an error
    print(" Done.")
    return synonyms


# Example function to get a tag ID given its name
def _get_tag_id(cur: psycopg.Cursor, tag_name: str) -> int | None:
    """
    Get the id of a tag from the database by the tags' name.
    :param cur:         psycopg database cursor
    :param tag_name:    The name of the tag
    :return:            The id if the tag was found, otherwise None.
    """
    cur.execute("SELECT Id FROM Tags WHERE TagName = %s", (tag_name,))
    result = cur.fetchone()
    return result[0] if result else None


def store_tag_synonyms(synonyms: List[TagSynonymMapping]) -> None:
    """
    Store a list of tag synonym mappings to the database.
    :param synonyms:    The tag synonym mapping list from the StackExchange API
    :return:
    """

    print("Storing tag synonyms in database...")
    conn = psycopg.connect(**POSTGRES_CONFIG)
    cur = conn.cursor()

    # Ensure the TagSynonyms table exists
    cur.execute("""
            CREATE TABLE IF NOT EXISTS TagSynonyms (
                PrimaryTagId INTEGER,
                SynonymTagId INTEGER,
                FOREIGN KEY (PrimaryTagId) REFERENCES Tags(Id),
                FOREIGN KEY (SynonymTagId) REFERENCES Tags(Id),
                UNIQUE(PrimaryTagId, SynonymTagId)
            );
        """)
    conn.commit()

    for idx, synonym in enumerate(synonyms):
        primary_tag_id = _get_tag_id(cur, synonym['to_tag'])
        synonym_tag_id = _get_tag_id(cur, synonym['from_tag'])

        if primary_tag_id and synonym_tag_id:
            try:
                cur.execute(
                    "INSERT INTO TagSynonyms (PrimaryTagId, SynonymTagId) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (primary_tag_id, synonym_tag_id)
                )
            except psycopg.Error as e:
                print(f"Error inserting synonym {synonym}: {e}")
        else:
            if not primary_tag_id:
                print(f"Tag not found in Tags table: {synonym['to_tag']}")
            if not synonym_tag_id:
                print(f"Tag not found in Tags table: {synonym['from_tag']}")
    conn.commit()

    cur.close()
    conn.close()


if __name__ == "__main__":
    synonyms_from_api = fetch_all_tag_synonyms()
    store_tag_synonyms(synonyms_from_api)
