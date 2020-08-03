# BMPMOT
BMPMan One Touch

A fully CLI based version of the old BMPMAN I built, works much faster and continues to improve with every release.

## Changes

* Removed GUI
* Removed threading (I/O heavy, not CPU heavy)
* Changed header to be C Compliant (64 Bytes over 128 Bytes double encoded)
* Added metafile creation
* Creates item specific output directory
* Works on multiple files at once
* Reoved the use/need of creating items in USER's HOME directory

## Usage

./BMPMOT -c [INT] -i [DIR] -o [DIR]

Chunk is usually not changed, but defaults to what google and most vendors should accept. If the limit gets removed, you can up the chunk size

Input is the directory you choose for input, it must contain files (preferably zip archives or large files), defaults to ./INPUT

Output is the directory you choose for output, subdirectories will be made contaning BMP files for each file (and the meta file), defaults to ./OUTPUT

To rebuild a file, the Input directory must be the directory containing both the BMPFILE and BMP files made with this program.

## Limitations

Limited windows support, windows is not great at handling the basic tasks this tries to accomplish...

Currently, in an effort to keep things short on the actual program side, I opted to not sanitize names too heavily, as a side effect, any image containing special characters "!@#$%^&*()_+-={}[]|\\;:'"/?><~`" will likely not be able to be turned back into a file, as well as files with names having multiple periods having slightly messed up output folders.
