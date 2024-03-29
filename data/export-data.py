import psycopg
import json

from config import POSTGRES_CONFIG

TAG_PAIR_COUNT_THRESHOLD = 2500
TAG_PAIR_SCORE_THRESHOLD = 0.05


def export_data():
    conn = psycopg.connect(**POSTGRES_CONFIG)
    cur = conn.cursor()

    print("Exporting tag and tag-pair count and score data from database...")

    # Select tag pairs with PairCount > TAG_PAIR_COUNT_THRESHOLD
    cur.execute("""
        SELECT Tag1, Tag2, PairCount
        FROM TagPairCounts
        WHERE PairCount > %s
    """, (TAG_PAIR_COUNT_THRESHOLD,))
    tag_pair_counts = [{"tag1": row[0], "tag2": row[1], "pairCount": row[2]} for row in cur.fetchall()]

    # Select tag pairs with PairScore > TAG_PAIR_SCORE_THRESHOLD
    cur.execute("""
            SELECT Tag1, Tag2, NormalizedScore
            FROM TagPairScores
            WHERE NormalizedScore > %s
        """, (TAG_PAIR_SCORE_THRESHOLD,))
    tag_pair_scores = [{"tag1": row[0], "tag2": row[1], "pairScore": row[2]} for row in cur.fetchall()]

    # Select all tags present in the filtered TagPairCounts table
    cur.execute("""
        SELECT t.TagName, t.Count
        FROM Tags t
        WHERE EXISTS (
            SELECT 1 FROM TagPairCounts tpc
            WHERE (tpc.Tag1 = t.TagName OR tpc.Tag2 = t.TagName)
            AND tpc.PairCount > %s
        )
    """, (TAG_PAIR_COUNT_THRESHOLD,))
    count_tags = [{"tagName": row[0], "count": row[1]} for row in cur.fetchall()]

    # Select all tags present in the filtered TagPairScores table
    cur.execute("""
        SELECT t.TagName, t.Count
        FROM Tags t
        WHERE EXISTS (
            SELECT 1 FROM TagPairScores tpc
            WHERE (tpc.Tag1 = t.TagName OR tpc.Tag2 = t.TagName)
            AND tpc.NormalizedScore > %s
        )
    """, (TAG_PAIR_SCORE_THRESHOLD,))
    score_tags = [{"tagName": row[0], "count": row[1]} for row in cur.fetchall()]

    # Close the database connection
    cur.close()
    conn.close()

    # Save the results to JSON files
    with open('./result/tag-pair-counts.json', 'w') as f:
        json.dump(tag_pair_counts, f)

    with open('./result/tag-pair-scores.json', 'w') as f:
        json.dump(tag_pair_scores, f)

    with open('./result/count-tags.json', 'w') as f:
        json.dump(count_tags, f)

    with open('./result/score-tags.json', 'w') as f:
        json.dump(score_tags, f)


if __name__ == '__main__':
    export_data()
