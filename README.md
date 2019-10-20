# BMPMOT
BMPMan One Touch, quick and easy data injection

This is a trimmed down and better documented version of the now legacy BMPMAN

## Changes

* Removed GUI
* Removed hashing
* Removed innefficient threading
* Changed header to be C Compliant (64 Bytes over 128 Bytes double encoded)
* Added metafile creation
* Creates item specific output directory
* Works on multiple files at once
* Reoved the use/need of creating items in USER's HOME directory
* No longer windows friendly out of the box (change "/" to "\\\\" for that)

## Usage

### Create bitmap files

* Run BMPMOT
* Put data into newly created Input directory
* View files in "Output/{Your file name}/*}

### Creating files from bitmaps

* Put bitmaps, including *.bmpfile.bmp files
* Run BMPMOT
* Check "Output/*" for recreated files

## Limitations

Currently, in an effort to keep things short on the actual program side, I opted to not sanitize names too heavily, as a side effect, any image containing special characters "!@#$%^&*()_+-={}[]|\\;:'"/?><~`" will likely not be able to be turned back into a file, as well as files with names having multiple periods having slightly messed up output folders.
