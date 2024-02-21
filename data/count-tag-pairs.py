import psycopg

from config import POSTGRES_CONFIG


def count_tag_pairs() -> None:
    conn = psycopg.connect(**POSTGRES_CONFIG, autocommit=True)
    cur = conn.cursor()

    sql_file = open('count-tag-pairs.sql', 'r')

    print("Generating table for tag-pair counts...")
    cur.execute(sql_file.read())


if __name__ == "__main__":
    count_tag_pairs()
