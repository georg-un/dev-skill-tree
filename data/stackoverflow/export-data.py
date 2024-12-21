import psycopg
import json

from stackoverflow.config import POSTGRES_CONFIG

TAG_COUNT_THRESHOLD = 5000


def export_data():
    conn = psycopg.connect(**POSTGRES_CONFIG)
    cur = conn.cursor()

    print("Exporting tag and tag-pair count and score data from database...")

    sql_file = open('resolve-tags.sql', 'r')
    cur.execute(sql_file.read())
    resolved_tags = [{"tag": row[0], "count": row[1]} for row in cur.fetchall()]

    # Select all tag pairs
    cur.execute("SELECT Tag1, Tag2, PairCount, NormalizedScore FROM TagPairScores")
    tag_pairs = [{
        "tag1": row[0],
        "tag2": row[1],
        "pairCount": row[2],
        "pairCountNormalized": row[3]
    } for row in cur.fetchall()]

    # Close the database connection
    cur.close()
    conn.close()

    # Filter the data according to the count threshold
    resolved_tags = [tag for tag in resolved_tags if tag['count'] > TAG_COUNT_THRESHOLD]
    tag_names = [tag['tag'] for tag in resolved_tags]
    tag_pairs = [pair for pair in tag_pairs if pair['tag1'] in tag_names and pair['tag2'] in tag_names]

    print(f"Number of tags: {len(resolved_tags)}.")
    print(f"Number of tag-pairs: {len(tag_pairs)}.")

    # Save the results to JSON files
    with open('result/tag-pairs.json', 'w') as file:
        json.dump(tag_pairs, file, indent=2)

    with open('result/tags.json', 'w') as file:
        json.dump(resolved_tags, file, indent=2)


if __name__ == '__main__':
    export_data()
