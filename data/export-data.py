import psycopg
import json

from config import POSTGRES_CONFIG

TAG_PAIR_COUNT_THRESHOLD = 2500


def export_data():
    conn = psycopg.connect(**POSTGRES_CONFIG)
    cur = conn.cursor()

    print("Exporting tag and tag-pair count data from database...")

    # Select tag pairs with PairCount > TAG_PAIR_COUNT_THRESHOLD
    cur.execute("""
        SELECT Tag1, Tag2, PairCount
        FROM TagPairCounts
        WHERE PairCount > %s
    """, (TAG_PAIR_COUNT_THRESHOLD,))
    tag_pair_counts = [{"tag1": row[0], "tag2": row[1], "pairCount": row[2]} for row in cur.fetchall()]

    # Select only tags present in the filtered TagPairCounts table
    cur.execute("""
        SELECT t.TagName, t.Count
        FROM Tags t
        WHERE EXISTS (
            SELECT 1 FROM TagPairCounts tpc
            WHERE (tpc.Tag1 = t.TagName OR tpc.Tag2 = t.TagName)
            AND tpc.PairCount > %s
        )
    """, (TAG_PAIR_COUNT_THRESHOLD,))
    tags = [{"tagName": row[0], "count": row[1]} for row in cur.fetchall()]

    # Close the database connection
    cur.close()
    conn.close()

    # Save the results to JSON files
    with open('./result/tag-pair-counts.json', 'w') as f:
        json.dump(tag_pair_counts, f)

    with open('./result/tags.json', 'w') as f:
        json.dump(tags, f)


if __name__ == '__main__':
    export_data()
