# Data

Python project to download and transform the StackOverflow data from the [StackExchange dump (SEDE)](https://archive.org/download/stackexchange) on archive.org.

For an in-depth explanation of the database schema, see [the documentation](https://meta.stackexchange.com/questions/2677/database-schema-documentation-for-the-public-data-dump-and-sede) on StackExchange.

## Prerequisites

Libraries and tools required for this guide:

- Python 3.10 (other versions might work as well)
- [virtualenv](https://virtualenv.pypa.io/en/latest/) (for the creation of the Python environment)
- [SQLite](https://www.sqlite.org/index.html)

Additionally, you need around **150GB** free space on your hard drive.

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
   
## Usage

For the full data pipeline, execute the following steps in the same order as they are listed here.

1. ### Download the data
   - #### Option 1: Download the data via torrent **(recommended)**:
      1. You can download the torrent file [here](https://archive.org/download/stackexchange/stackexchange_archive.torrent).
      2. Don't download the full archive but only the following files:
         - _stackoverflow.com-Badges.7z,_
         - _stackoverflow.com-Comments.7z_,
         - _stackoverflow.com-PostHistory.7z_,
         - _stackoverflow.com-PostLinks.7z_,
         - _stackoverflow.com-Posts.7z_,
         - _stackoverflow.com-Tags.7z_,
         - _stackoverflow.com-Users.7z_,
         - _stackoverflow.com-Votes.7z_,
      3. After the download is complete, extract the files and place them in the folder [/raw](./raw).
   - #### Option 2: Download the data with the downloader script:
      1. To download the StackOverflow dump from archive.org directly, you need to set your access credentials. 
         First, create an account on [archive.org](https://archive.org). 
      2. Follow [this guide](https://archive.org/developers/tutorial-get-ia-credentials.html#steps) to generate your credentials. 
         Subsequently, set the respective values in [keys.py](./keys.py).
      3. Execute the downloader script to download the data:   
         ```bash
         python ./download.py
         ```
         Note: The dump has a size of around **60GB** and archive.org does not offer high bandwidth downloads. 
         Depending on where you live and how busy their servers are at the moment, this will either just take a very long time or fail completely.
2. ### Create an SQLite database and load the data into it
   ```bash
   python ./load-into-db.py
   ```
