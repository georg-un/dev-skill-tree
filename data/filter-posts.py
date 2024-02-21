import psycopg

from config import POSTGRES_CONFIG


def filter_posts() -> None:
    conn = psycopg.connect(**POSTGRES_CONFIG, autocommit=True)
    cur = conn.cursor()

    sql_file = open('filter-posts.sql', 'r')

    print("Generating table with filtered posts...")
    cur.execute(sql_file.read())


if __name__ == "__main__":
    filter_posts()
