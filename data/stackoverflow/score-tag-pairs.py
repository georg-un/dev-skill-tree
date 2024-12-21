import psycopg

from stackoverflow.config import POSTGRES_CONFIG


def score_tag_pairs() -> None:
    conn = psycopg.connect(**POSTGRES_CONFIG, autocommit=True)
    cur = conn.cursor()

    sql_file = open('score-tag-pairs.sql', 'r')

    print("Generating table for normalized tag-pair scores...")
    cur.execute(sql_file.read())


if __name__ == "__main__":
    score_tag_pairs()
