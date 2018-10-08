# pymediamgmt
Tools for managing a media library such as extracting downloaded RAR archives automatically into an organized directory structure.

# autoMatchExtract

This script is intended to comb through a folder for RAR files representing movies or TV shows and determine where they should be extracted.  It is intended to be used as a download completion trigger.

It has been built for Windows.

## Requirements
`pip3 install fuzzywuzzy python-Levenshtein pathlib`

[Visual CPP build tools (for levenshtein)](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2017)


## Usage
To extract RARs
`python autoMatchExtract.py -x -s "<library base path to search>" -t "<folder name for TV shows>" -m "<folder name for movies>" -z "<path to 7zip executable>"`
Where...
* `<library base path to search>` is the root directory where RAR archives can be found as well as where extracted contents are organized
* `<folder name for TV shows>` is the folder in base path where TV shows are organized
* `<folder name for movies>` is the folder in base path where movies are organized
* `<path to 7zip exe>` is where 7z.exe can be found
  
This will result in, for example, a file `C:\library\tv\Shameless.us.S01E02.[...].rar' will have its contents extracted to a folder c:\library\tv\Shameless\S01\
