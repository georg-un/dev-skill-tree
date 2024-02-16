import sqlite3
import os
import xml.etree.cElementTree as etree
import logging

from download import DOWNLOAD_FOLDER


DATABASE_NAME = "stackoverflow.db"
LOGFILE_PATH = "/tmp/2-to-db.log"

TABLE_SCHEMAS = {
    # 'Badges': {
    #     'Id': 'INTEGER',
    #     'UserId': 'INTEGER',
    #     'Class': 'INTEGER',
    #     'Name': 'TEXT',
    #     'Date': 'DATETIME',
    #     'TagBased': 'BOOLEAN',
    # },
    # 'Comments': {
    #     'Id': 'INTEGER',
    #     'PostId': 'INTEGER',
    #     'Score': 'INTEGER',
    #     'Text': 'TEXT',
    #     'CreationDate': 'DATETIME',
    #     'UserId': 'INTEGER',
    #     'UserDisplayName': 'TEXT'
    # },
    # 'Posts': {
    #     'Id': 'INTEGER',
    #     'PostTypeId': 'INTEGER',  # 1: Question, 2: Answer
    #     'ParentId': 'INTEGER',  # (only present if PostTypeId is 2)
    #     'AcceptedAnswerId': 'INTEGER',  # (only present if PostTypeId is 1)
    #     'CreationDate': 'DATETIME',
    #     'Score': 'INTEGER',
    #     'ViewCount': 'INTEGER',
    #     'Body': 'TEXT',
    #     'OwnerUserId': 'INTEGER',  # (present only if user has not been deleted)
    #     'OwnerDisplayName': 'TEXT',
    #     'LastEditorUserId': 'INTEGER',
    #     'LastEditorDisplayName': 'TEXT',  # ="Rich B"
    #     'LastEditDate': 'DATETIME',  # ="2009-03-05T22:28:34.823"
    #     'LastActivityDate': 'DATETIME',  # ="2009-03-11T12:51:01.480"
    #     'CommunityOwnedDate': 'DATETIME',  # (present only if post is community wikied)
    #     'Title': 'TEXT',
    #     'Tags': 'TEXT',
    #     'AnswerCount': 'INTEGER',
    #     'CommentCount': 'INTEGER',
    #     'FavoriteCount': 'INTEGER',
    #     'ClosedDate': 'DATETIME',
    #     'ContentLicense': 'TEXT'
    # },
    # 'Votes': {
    #     'Id': 'INTEGER',
    #     'PostId': 'INTEGER',
    #     'UserId': 'INTEGER',
    #     'VoteTypeId': 'INTEGER',
    #     # -   1: AcceptedByOriginator
    #     # -   2: UpMod
    #     # -   3: DownMod
    #     # -   4: Offensive
    #     # -   5: Favorite
    #     # -   6: Close
    #     # -   7: Reopen
    #     # -   8: BountyStart
    #     # -   9: BountyClose
    #     # -  10: Deletion
    #     # -  11: Undeletion
    #     # -  12: Spam
    #     # -  13: InformModerator
    #     'CreationDate': 'DATETIME',
    #     'BountyAmount': 'INTEGER'
    # },
    # 'PostHistory': {
    #     'Id': 'INTEGER',
    #     'PostHistoryTypeId': 'INTEGER',
    #     'PostId': 'INTEGER',
    #     'RevisionGUID': 'TEXT',
    #     'CreationDate': 'DATETIME',
    #     'UserId': 'INTEGER',
    #     'UserDisplayName': 'TEXT',
    #     'Comment': 'TEXT',
    #     'Text': 'TEXT'
    # },
    # 'PostLinks': {
    #     'Id': 'INTEGER',
    #     'CreationDate': 'DATETIME',
    #     'PostId': 'INTEGER',
    #     'RelatedPostId': 'INTEGER',
    #     'PostLinkTypeId': 'INTEGER',
    #     'LinkTypeId': 'INTEGER'
    # },
    # 'Users': {
    #     'Id': 'INTEGER',
    #     'Reputation': 'INTEGER',
    #     'CreationDate': 'DATETIME',
    #     'DisplayName': 'TEXT',
    #     'LastAccessDate': 'DATETIME',
    #     'WebsiteUrl': 'TEXT',
    #     'Location': 'TEXT',
    #     'Age': 'INTEGER',
    #     'AboutMe': 'TEXT',
    #     'Views': 'INTEGER',
    #     'UpVotes': 'INTEGER',
    #     'DownVotes': 'INTEGER',
    #     'AccountId': 'INTEGER',
    #     'ProfileImageUrl': 'TEXT'
    # },
    'Tags': {
        'Id': 'INTEGER',
        'TagName': 'TEXT',
        'Count': 'INTEGER',
        'ExcerptPostId': 'INTEGER',
        'WikiPostId': 'INTEGER'
    }
}


def load_files_into_db(file_names,
                       table_schemas,
                       directory,
                       database_name,
                       log_filename=LOGFILE_PATH):
    """
    Function to create a new SQLite database and load StackOverflow XML dump files into it.

    This code has been blatantly copied from https://meta.stackexchange.com/a/286488 and slightly modified.

    :param file_names:          Names of the XML files without the .xml file ending
    :param table_schemas:       SQL schemas the respective tables
    :param directory:           Path to the downloaded XML files
    :param database_name:       Name that will be used for the newly created database
    :param log_filename:        Filename for the log file
    """
    create_query = 'CREATE TABLE IF NOT EXISTS {table} ({fields})'
    insert_query = 'INSERT INTO {table} ({columns}) VALUES ({values})'

    logging.basicConfig(filename=os.path.join(directory, log_filename), level=logging.INFO)
    db = sqlite3.connect(os.path.join(directory, database_name))
    for file in file_names:
        print("Opening {0}.xml".format(file))
        with open(os.path.join(directory, file + '.xml')) as xml_file:
            tree = etree.iterparse(xml_file)
            table_name = file

            sql_create = create_query.format(
                table=table_name,
                fields=", ".join(['{0} {1}'.format(name, type) for name, type in table_schemas[table_name].items()]))
            print('Creating table {0}'.format(table_name))

            try:
                logging.info(sql_create)
                db.execute(sql_create)
            except Exception as e:
                logging.warning(e)

            count = 0
            for events, row in tree:
                try:
                    if row.attrib.values():
                        logging.debug(row.attrib.keys())
                        query = insert_query.format(
                            table=table_name,
                            columns=', '.join(row.attrib.keys()),
                            values=('?, ' * len(row.attrib.keys()))[:-2])
                        vals = []
                        for key, val in row.attrib.items():
                            if table_schemas[table_name][key] == 'INTEGER':
                                vals.append(int(val))
                            elif table_schemas[table_name][key] == 'BOOLEAN':
                                vals.append(1 if val == "TRUE" else 0)
                            else:
                                vals.append(val)
                        db.execute(query, vals)

                        count += 1
                        if count % 1000 == 0:
                            print("{}".format(count))

                except Exception as e:
                    logging.warning(e)
                    print("x", end="")
                finally:
                    row.clear()
            print("\n")
            db.commit()
            del tree


if __name__ == '__main__':
    load_files_into_db(TABLE_SCHEMAS.keys(), TABLE_SCHEMAS, DOWNLOAD_FOLDER, DATABASE_NAME)
