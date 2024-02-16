# Data

Python project to download and transform the StackOverflow data from the [StackExchange dump (SEDE)](https://archive.org/download/stackexchange) on archive.org.

For an in-depth explanation of the database schema, see [the documentation](https://meta.stackexchange.com/questions/2677/database-schema-documentation-for-the-public-data-dump-and-sede) on StackExchange.

## Prerequisites

Libraries and tools required for this guide:

- Python 3.10 (other versions might work as well)
- [virtualenv](https://virtualenv.pypa.io/en/latest/) (for the creation of the Python environment)
- [SQLite](https://www.sqlite.org/index.html)

Additionally, for downloading the StackOverflow dump, you need to create an account at [archive.org](https://archive.org).

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
3. To download the StackOverflow dump from archive.org, you need to set your access credentials.
   Follow [this guide] to generate your credentials. Subsequently, set the respective values in [keys.py](./keys.py).
   
## Usage

For the full data pipeline, execute the following scripts in the same order as they are listed here.

1. Download the data
   ```bash
   python ./download.py
   ```
   **Note:** The dump has a size of around **40GB** and archive.org does not offer high bandwidth downloads. 
   This will take a very long time.
2. Create an SQLite database and load the data into it.
   ```bash
   python ./load-into-db.py
   ```
