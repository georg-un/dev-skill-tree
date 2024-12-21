import os

import internetarchive as ia
import py7zr
from dotenv import load_dotenv

DOWNLOAD_FOLDER = "raw/"

ARCHIVE = "stackexchange"

# see https://archive.org/download/stackexchange
FILES = (
    "stackoverflow.com-Posts.7z",
    "stackoverflow.com-Tags.7z",
    "stackoverflow.com-Users.7z",
)

# see https://internetarchive.readthedocs.io/en/stable/internetarchive.html#internetarchive.api.get_session
load_dotenv()
CONFIG = dict(s3=dict(access=os.getenv('INTERNET_ARCHIVE_ACCESS_KEY'), secret=os.getenv('INTERNET_ARCHIVE_SECRET_KET')))


def download_all_files(archive: str, files: tuple[str], dest_dir: str, config: dict) -> None:
    """
    Download and extract a list of files from an archive on archive.org.

    :param archive:     The archive name
    :param files:       Tuple of filenames that shall be downloaded from the archive
    :param dest_dir:    Destination directory for the downloaded files
    :param config:      Access configuration for archive.org
    """

    stackexchange = ia.get_item(archive, config=config)

    for filename in files:
        archive_path = f"{dest_dir}{filename}"
        try:
            print(f"Downloading {filename}...", end=" ")
            # download the archive
            archive_file = stackexchange.get_file(filename)
            archive_file.download(archive_path)
            # extract the file
            with py7zr.SevenZipFile(archive_path, 'r') as archive:
                archive.extractall(path=dest_dir)
            # delete the archive
            os.remove(archive_path)
            print("Done")
        except Exception as e:
            print(f"\nError while downloading {filename}:")
            print(e)


if __name__ == "__main__":
    download_all_files(ARCHIVE, FILES, DOWNLOAD_FOLDER, CONFIG)
