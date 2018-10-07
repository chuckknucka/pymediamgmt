import os
import re
import sys
import argparse
import subprocess
import logging
from pathlib import Path
from fuzzywuzzy import fuzz, process


def find_file(rootdir, filename):
    for dirpath, dirnames, filenames in os.walk(rootdir):
        if filename in filenames:
            return dirpath
    return None

def find_folder_fuzzy(rootdir, search, threshold=60):
    dirs = [p for p in os.listdir(rootdir) if os.path.isdir(os.path.join(rootdir, p))]
    if dirs:
        result = process.extractOne(search, dirs)
        if result[1] > threshold:
            return os.path.join(rootdir, result[0])
    return None

def find_season_path(show_path, season):
    dirs = [p.lower() for p in os.listdir(show_path) if os.path.isdir(os.path.join(show_path, p))]
    items = [season.lower(), season.lower().replace("s", "season"), season.lower().replace("s", "season ")]
    for item in items:
        if item in dirs:
            return item
    print (items, dirs)
    return None


def is_tv_show(filename):
    rx = re.compile(r'(\S+)([Ss]\d{2})([Ee]\d{2})(.*)')
    match = rx.match(filename)
    if match:
        return True
    return False

def parse_show(filename):
    rx = re.compile(r'(\S+)([Ss]\d{2})([Ee]\d{2})(.*)')
    match = rx.match(filename)
    if match:
        return match.groups()
    return None

logging.basicConfig(filename="{}.log".format(__file__), level=logging.DEBUG, format='%(asctime)s %(levelname)s:: %(message)s')
logging.debug("Arguments: %s", sys.argv)

path_7z = r"C:\Program Files\7-Zip\7z.exe"
base_search_path = r"f:\bin"
tv_folder_name = "[tv]"
movies_folder_name = "[movies]"

parser = argparse.ArgumentParser(description="Finds RARs and attempts to match their paths based on their names.")
parser.add_argument("-s", "--search", default=base_search_path, help="The path to search for contents of archives")
parser.add_argument("-z", "--p7zip", default=path_7z, help="Path to 7-zip")
parser.add_argument("-t", "--tv", default=tv_folder_name, help="Name of the folder in search path where TV shows are organized")
parser.add_argument("-m", "--movies", default=movies_folder_name, help="Name of the folder in search path where movies are organized")
parser.add_argument("-x", "--extract", action="store_true", help="Do extraction.")
parser.add_argument("-q", "--quiet", action="store_true", help="Show no output")
parser.add_argument("-k", "--skip_tv", action="store_true", help="Skip processing of TV shows")
parser.add_argument("-v", "--skip_movies", action="store_true", help="Skip processing of Movies")


args = parser.parse_args()

quiet = args.quiet
extract = args.extract
skip_tv = args.skip_tv
skip_movies = args.skip_movies
path_7z = args.p7zip
base_search_path = args.search
tv_folder_name = args.tv
movies_folder_name = args.movies
tv_search_path = os.path.join(base_search_path, tv_folder_name)
movies_search_path = os.path.join(base_search_path, movies_folder_name)

logging.debug("Base search path: %s", base_search_path)
logging.debug("TV folder: %s", tv_search_path)
logging.debug("Movies folder: %s", movies_search_path)

if not skip_tv:
    p = Path(tv_search_path)
    for rar in p.glob("**\\*.rar"):
        if not quiet:
            print("Found RAR: ", rar)
        logging.debug("Processing RAR: %s", rar)
        output = subprocess.check_output([path_7z, "l", str(rar)]).decode("utf-8")
        parts = output.split("\r\n")
        file_parts = parts[16:-3]
        for f in file_parts:
            filename = f.split("  ")[-1:][0]
            if not quiet:
                print("Processing ", filename, "in", rar, "...")
            logging.debug("Processing file '%s' in RAR '%s'", filename, rar)
            parent = find_file(base_search_path, filename)
            if is_tv_show(filename):
                show_parts = parse_show(filename)
                if not quiet:
                    print("\tDetermined TV Show as: ", show_parts[0])
                show_folder = find_folder_fuzzy(tv_search_path, show_parts[0])
                if show_folder:
                    season_folder = find_season_path(show_folder, show_parts[1])
                    if season_folder:
                        season_path = os.path.join(show_folder, season_folder)
                        if os.path.exists(season_path) and os.path.isdir(season_path):
                            if not quiet:
                                print("\tFound place to extract this show: ", season_path)
                            if parent:
                                if not quiet:
                                    print("\t\t...However, the file already exists in: ", parent)
                                logging.debug("No need to extract.  File already exists in %s", parent)
                            else:
                                if not quiet:
                                    print("\t\t...And, the file does not exist yet.")
                                logging.debug("File not found anywhere in search path.  Will extract to %s", season_path)
                                if extract:
                                    if not quiet:
                                        print("\t\tExtracting", rar, "to", season_path, "...")
                                    logging.debug("Beginning extraction of %s to %s", rar, season_path)
                                    result = subprocess.call([path_7z, "e", str(rar), "-y", "-o{}".format(season_path)])
                                    logging.debug("Extraction completed with result %d", result)
                    else:
                        if not quiet:
                            print("Could not find a season folder for ", show_folder)
                        logging.debug("Season folder not found for show %s", show_folder)

if not skip_movies:
    p = Path(movies_search_path)
    for rar in p.glob("**\\*.rar"):
        output = subprocess.check_output([path_7z, "l", str(rar)]).decode("utf-8")
        parts = output.split("\r\n")
        file_parts = parts[16:-3]
        for f in file_parts:
            filename = f.split("  ")[-1:][0]
            if not quiet:
                print("Processing ", filename, "in", rar, "...")
            logging.debug("Processing file '%s' in RAR '%s'", filename, rar)
            parent = find_file(base_search_path, filename)
            if not parent:
                logging.debug("File %s not found in %s.", filename, base_search_path)
                if extract:
                    if not quiet:
                        print("Extracting ", rar, "to", movies_search_path)
                    logging.debug("Beginning extraction of %s to %s", rar, movies_search_path)
                    result = subprocess.call([path_7z, "e", str(rar), "-y", "-o{}".format(movies_search_path)])
                    logging.debug("Extraction completed with result %d", result)
                else:
                    if not quiet:
                        print("Would extract ", rar, "to", movies_search_path)
                    logging.debug("Would extract %s to %s", rar, movies_search_path)
            else:
                logging.debug("Found %s in %s.  No extraction necessary.", filename, parent)