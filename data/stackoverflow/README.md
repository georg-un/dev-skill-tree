# StackOverflow data

Python project to download and transform the StackOverflow data from the [StackExchange dump (SEDE)](https://archive.org/download/stackexchange) on archive.org.

For an in-depth explanation of the database schema, see [the documentation](https://meta.stackexchange.com/questions/2677/database-schema-documentation-for-the-public-data-dump-and-sede) on StackExchange.

## Prerequisites

Libraries and tools required for this guide:

- Linux
- Python 3.10 (other versions might work as well)
- [virtualenv](https://virtualenv.pypa.io/en/latest/) (for the creation of the Python environment)
- [PostgreSQL](https://www.postgresql.org/)

Additionally, you need around **200GB** free space on your hard drive.

## Get started

1. Set up and activate a virtual environment.
   ```bash
   virtualenv env
   source env/bin/activate
   ```
2. Install all required packages.
   ```bash
   python install -r requirements.txt
   ````
3. Create a `.env` file with the required configuration (see [.env.template](./.env.template)).
   
## Usage

For the full data pipeline, execute the following steps in the same order as they are listed here.

1. ### Download the data
   - #### Option 1: Download the data via torrent **(recommended)**:
      1. You can download the torrent file [here](https://archive.org/download/stackexchange/stackexchange_archive.torrent).
      2. Don't download the full archive but only the following files:
         - _stackoverflow.com-Posts.7z_,
         - _stackoverflow.com-Tags.7z_,
         - _stackoverflow.com-Users.7z_,
      3. After the download is complete, extract the XML files and place them in the folder [raw/](raw).
   - #### Option 2: Download the data with the downloader script:
      1. To download the StackOverflow dump from archive.org directly, you need to set your access credentials. 
         First, create an account on [archive.org](https://archive.org). 
      2. Follow [this guide](https://archive.org/developers/tutorial-get-ia-credentials.html#steps) to generate your credentials. 
         Subsequently, set the respective values in [config.py](config.py).
      3. Execute the downloader script to download the data:   
         ```bash
         python ./download.py
         ```
         Note: the dump has a size of around **60GB** and archive.org does not offer high bandwidth downloads. 
         Depending on where you live and how busy their servers are at the moment, this will either just take a very long time or fail completely.
2. ### Create a Postgres database and load the data into it
   This guide uses _"postgres"_ as username and password and _"stackoverflow"_ as database name. If you want to use
   a different configuration, change the values of the `POSTGRES_CONFIG` variable in [config.py](config.py) and
   adjust the commands in the following steps accordingly.
   1. First, create a new database:
      ```bash
      sudo -u postgres psql -c 'create database stackoverflow;'
      ```
   2. Grant all privileges of the new database to the user _postgres_:
      ```bash
      sudo -u postgres psql -c 'grant all privileges on database stackoverflow to postgres;'
      ```
   3. Run the script to load the data from the XML files into the database:
      ```bash
      python ./load-into-db.py
      ```
      Note: this step will probably take multiple hours.
3. ### Download the tag synonyms
   Tags can be synonyms for other tags but, as of now, this mapping is not included in the StackExchange data dump.
   Therefore, we have to fetch it from the StackExchange API and write it to the database ourselves.
   To do that, run the following script:  
   ```bash
   python ./get-tag-synonyms.py
   ```
   Note: since the data in your database is probably a few months old, the API will return some tags that don't exist
   yet in the database. These tags will be ignored and the info `Tag not found in Tags table: <tag-name>` 
   will be printed to the console. This is expected and just for your info.
4. ### Filter the posts
   Currently, the posts include answers to questions, closed questions, old and inactive questions, 
   and questions with a negative score. Generate a table that contains only clean data by running:
   ```bash
   python ./filter-posts.py
   ```
5. ### Calculate the tag-pair scores
   Weighting the tag-pair counts by how many times both tags are referenced in the dataset overall tends to yield better results.
   We call these weighted counts the "scores" of the tag-pairs. To calculate them, run:
   ```bash
   python ./score-tag-pairs.py
   ```
6. ### Export the data
   Export the tags and the tag-pair counts as JSON with:
   ```bash
   python ./export-data.py
   ```
   This will create the files `tags.json` and `tag-pairs.json` in the folder [result/](result).
7. ### Calculate the weight
   To stay flexible with how the weight is calculated, we have a separate step for that:
   ```bash
   python ./calculate-weight.py
   ```
8. ### Generate the clusters
   Next, we perform a hierarchical clustering:
   ```bash
   python ./cluster.py
   ```

## Filters

The following filters are used in the course of the data pipeline and have an impact on the final result:

- In [step 4](README.mdilter-the-posts), before counting the tag pairs:
  - Closed questions are removed.
  - Questions with a score lower than `-1` are removed.
  - Questions with no activity after `2018-01-01` are removed.
- In [step 6](README.mdxport-the-data), when generating the result JSONs:
  - There's a tag count threshold of `5000`. 
  - Tags with a count smaller than the threshold are removed.
  - Tag pairs where one of the tags has a count smaller than the threshold are removed.
