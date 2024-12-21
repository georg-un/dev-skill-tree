import logging
import os
import xml.etree.cElementTree as etree
from collections.abc import KeysView

import psycopg

from stackoverflow.config import POSTGRES_CONFIG
from download import DOWNLOAD_FOLDER

LOGFILE_PATH = "/tmp/load-into-db.log"

TABLE_SCHEMAS = {
    'Posts': {
        'Id': 'INTEGER PRIMARY KEY',
        'PostTypeId': 'INTEGER',  # 1: Question, 2: Answer
        'ParentId': 'INTEGER',
        'AcceptedAnswerId': 'INTEGER',
        'CreationDate': 'TIMESTAMP',
        'Score': 'INTEGER',
        'ViewCount': 'INTEGER',
        'Body': 'TEXT',
        'OwnerUserId': 'INTEGER',  # (present only if user has not been deleted)
        'OwnerDisplayName': 'TEXT',
        'LastEditorUserId': 'INTEGER',
        'LastEditorDisplayName': 'TEXT',
        'LastEditDate': 'TIMESTAMP',
        'LastActivityDate': 'TIMESTAMP',
        'CommunityOwnedDate': 'TIMESTAMP',
        'Title': 'TEXT',
        'Tags': 'TEXT',
        'AnswerCount': 'INTEGER',
        'CommentCount': 'INTEGER',
        'FavoriteCount': 'INTEGER',
        'ClosedDate': 'TIMESTAMP',
        'ContentLicense': 'TEXT'
    },
    'Users': {
        'Id': 'INTEGER PRIMARY KEY',
        'Reputation': 'INTEGER',
        'CreationDate': 'TIMESTAMP',
        'DisplayName': 'TEXT',
        'LastAccessDate': 'TIMESTAMP',
        'WebsiteUrl': 'TEXT',
        'Location': 'TEXT',
        'Age': 'INTEGER',
        'AboutMe': 'TEXT',
        'Views': 'INTEGER',
        'UpVotes': 'INTEGER',
        'DownVotes': 'INTEGER',
        'AccountId': 'INTEGER',
        'ProfileImageUrl': 'TEXT'
    },
    'Tags': {
        'Id': 'INTEGER PRIMARY KEY',
        'TagName': 'TEXT',
        'Count': 'INTEGER',
        'ExcerptPostId': 'INTEGER',
        'WikiPostId': 'INTEGER'
    },
}


def load_files_into_db(
        file_names: KeysView,
        table_schemas: dict,
        directory: str,
        database_params: dict,
        log_filename=LOGFILE_PATH
) -> None:
    """
    Function to create a new PostgreSQL database and load StackOverflow XML dump files into it.

    This code has been blatantly copied from https://meta.stackexchange.com/a/286488 and heavily modified.

    :param file_names:          Names of the XML files without the .xml file ending
    :param table_schemas:       SQL schemas the respective tables
    :param directory:           Path to the downloaded XML files
    :param database_params:     Dictionary with database connection parameters
    :param log_filename:        Filename for the log file
    """
    create_query = 'CREATE TABLE IF NOT EXISTS {table} ({fields})'
    insert_query = 'INSERT INTO {table} ({columns}) VALUES ({values})'

    logging.basicConfig(filename=os.path.join(directory, log_filename), level=logging.INFO)

    try:
        conn = psycopg.connect(**database_params)
    except Exception as e:
        logging.error(e)
        print(f"Unable to connect to the database:\n{e}")
        return

    cur = conn.cursor()
    for file in file_names:
        print("Opening {0}.xml".format(file))
        with open(os.path.join(directory, file + '.xml')) as xml_file:
            tree = etree.iterparse(xml_file)
            table_name = file

            fields_definitions = ", ".join([f'{name} {type}' for name, type in table_schemas[table_name].items()])
            sql_create = create_query.format(table=table_name, fields=fields_definitions)
            print(f'Creating table {table_name}')

            try:
                logging.info(sql_create)
                cur.execute(sql_create)
            except Exception as e:
                logging.warning(e)
                print(f"Error while creating table {table_name}:\n{e}")

            count = 0
            for events, row in tree:
                try:
                    if row.attrib.values():
                        columns = ', '.join(row.attrib.keys())
                        placeholders = ', '.join(['%s'] * len(row.attrib.keys()))
                        query = insert_query.format(table=table_name, columns=columns, values=placeholders)
                        vals = [val if table_schemas[table_name][key] not in ['INTEGER', 'BOOLEAN'] else int(val) for
                                key, val in row.attrib.items()]
                        cur.execute(query, vals)

                        count += 1
                        if count % 10000 == 0:
                            print(f"{table_name} total rows: {count}")
                            conn.commit()

                except Exception as e:
                    logging.warning(e)
                    print(f"Error while adding rows to table {table_name}:\n{e}")
                finally:
                    row.clear()

            conn.commit()
            del tree

    cur.close()
    conn.close()


if __name__ == '__main__':
    load_files_into_db(TABLE_SCHEMAS.keys(), TABLE_SCHEMAS, DOWNLOAD_FOLDER, POSTGRES_CONFIG)
