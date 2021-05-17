import os
import glob
import sys
import argparse
import json
import hashlib
import time
# import pathlib

VERSION: str = "1.0.5"

"""
Parse out pre-determined acceptable arguments
Also stores smaller functions and constant variables to be used by all lower functions
"""
apm = argparse.ArgumentParser(prog='BMPMOT')
apm.add_argument("--input", "-i", default="./INPUT", metavar="DIR", type=str, help="Directory of input file(s)")
apm.add_argument("--output", "-o", default="./OUTPUT", metavar='DIR', type=str, help="Output directory")
apm.add_argument("--chunk", '-c', metavar='INT', default=48000000, type=int, help="Size to split data")
apm.add_argument('--version', "-v", action='version', version=f'%(prog)s {VERSION}')
args = vars(apm.parse_args())
_INPUT_ = args['input']
_OUTPUT_ = args['output']

# Header compliant with C based languages
compliant_header = b'BM\xd2\xe4\xde\x02\x00\x00\x00\x00z\x00\x00\x00l\x00\x00\x007\x13\x00\x00\xbf\x0c\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00X\xe4\xde\x02\x13\x0b\x00\x00\x13\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00BGRs\x00\x00\x00\x00\x00\x00'

# Create an instance of time.time() without reference to function directly
now = time.time

# Create an instance of glob.glob() without reference to function directly
dir_list = glob.glob

# Check path existance without a direct call cost
exist = os.path.exists


def averages(chunk_size: int, clock1: float, clock2: float) -> float:  # Return average data output per second
    """
    :param chunk_size: Size of data chunk
    :param clock1: Start of read/write processes
    :param clock2: End of read/write processes
    :return: MegaBytes Read/Write per second based on chunk output per second
    """
    megabyte: float = 1.049e+6
    return float(round((chunk_size / (megabyte * (clock2 - clock1))), 2))


def delete(root: str) -> None:  # Delete files natively
    """
    :param root: Root directory or file to be deleted
    :return: No return, not an object
    """
    try:
        os.remove(f"{root}")
    except FileNotFoundError:
        pass


def chunk(file_size: int, raw_name: str, chunk_size: int = args['chunk'], input_dir: str = _INPUT_, output_dir: str = _OUTPUT_) -> None:
    """
    :param file_size: Original file size in bytes
    :param raw_name: The raw file name, such as 'File.fil'
    :param chunk_size: User/Default chunk size as INT
    :param input_dir: Directory used for input, user or Default
    :param output_dir: Directory used for output, user or Default
    :return: None, function does not return any data
    """
    print("Reading Data...")
    output_dir_u: str = f"{output_dir}/{raw_name[:-4]}/"
    whole_chunks: int = int(file_size) // int(chunk_size)  # Even divisible number of chunks in file
    remainder: int = int(file_size) % int(chunk_size)  # remaining data after chunks
    whole_chunks += 1 if remainder != 0 else 0  # Add another counter to whole chunks so as not to skip remaining data
    Hash_values: dict = {}  # Table of hash values
    # print(output_dir_u)

    if not exist(output_dir_u):  # Create the file specific directory if it does not already exist, usually it won't
        os.mkdir(output_dir_u)

    with open(f"{input_dir}/{raw_name}", 'rb') as core_file:  # Open the main file in bytes mode to allow reading raw data
        for i in range(whole_chunks):  # iterate over the file in chunks to process data
            read_clock1: float = now()  # First clock of read
            chunk_data: bytes = core_file.read(chunk_size)  # Store chunk's worth of data in memory
            name: str = create_bmp(chunk_data=chunk_data, iteration=i, raw_name=raw_name)  # create BMP file and return name to parent
            print(f"Created: {name}")
            Hash_values[f"{name}"]: str = hash_module(chunk_data)  # Store hash of newly created BMP file
            print(f"Hash: {Hash_values[f'{name}']}")
            read_clock2: float = now()  # End clock for read
            print(f"{averages(chunk_size=chunk_size, clock1=read_clock1, clock2=read_clock2)} MB/s AVERAGE\nCreating MetaData...")
    create_meta(file_size=file_size, hash_table=Hash_values, file_number=whole_chunks, raw_name=raw_name, chunk_size=chunk_size)  # Create metadata to allow for safe file rebuild


def create_bmp(chunk_data: bytes, iteration: int, raw_name: str, output_dir: str = _OUTPUT_) -> str:
    """
    :param chunk_data: Chunk of raw byte data provided by function chunk
    :param iteration: The iteration counter, from 0 to EOF in chunks (or from 0 to whole chunks)
    :param raw_name: The raw file name, such as 'File.fil'
    :param output_dir: User determined or Default output directory
    :return: Return name of newly created BMP file
    """
    delete(f"{output_dir}/{raw_name[:-4]}/{raw_name}.{iteration}.bmp")  # Delete duplicate BMP if present
    with open(f"{output_dir}/{raw_name[:-4]}/{raw_name}.{iteration}.bmp", "wb+") as bmp_data:  # Open a BMP in Output/FileName/file.{0-00000}.bmp
        bmp_data.write(compliant_header)  # Attach header
        bmp_data.write(chunk_data)  # Flush data
        bmp_data.close()  # Close and clean memory
    return f"{raw_name}.{iteration}.bmp"


def demake_bmpx(meta_file: str, input_dir: str = _INPUT_, output_dir: str = _OUTPUT_) -> None:
    """
    :param meta_file: File used for storing meta data, usually contains bmpfile in its title
    :param input_dir: User or default directory for input data
    :param output_dir: User or default directory for input data
    :return: None, does not return any data for other functions
    """
    meta: dict = parse_meta(meta_file)  # geta all values stored in meta file
    create_version: str = meta['VERSION']
    if create_version != VERSION:
        print("WARNING: Image set created ith different BMPMOT version; Build process may fail!")
        print("\nTo Proceed, type 'continue', otherwise hit 'enter' to exit\n")
        user_input: str = input("Action: ")
        if user_input != 'continue':
            sys.exit()
    master_file: str = f"{output_dir}/{meta['NAME']}"  # Name of main file as it is stored in meta
    delete(master_file)  # Attempt to delete the above file if it is already present
    hash_table: dict = eval(meta["HASHES"])  # Convert hash table from string into Dict of hashes
    count: int = int(meta["FILES"])  # Get the number of files from the meta file (chunks used to build original)
    with open(master_file, 'ab+') as output_file:  # Open the end file to have its data rebuilt
        write_clock1: float = now()  # First clock for write cycle
        for i in range(count):  # Iterate over count provided by meta data
            file_name_micro: str = f"{meta['NAME']}.{i}.bmp"  # Temporarily store BMP name to be used multiple times instead of rebuilding every time
            bmp_file: str = f"{input_dir}/{file_name_micro}"  # The BMP file being processed in the input directory
            with open(bmp_file, 'rb') as temp_data:  # Open BMP file to be processed and hashed
                file_data: bytes = temp_data.read()[64:]  # Skip header bytes as they were not included in original hash
                if hash_module(file_data) == hash_table[f"{file_name_micro}"]:  # If the hashes match, continue
                    print(f"Processing File: {file_name_micro} {i+1}/{count}")
                    output_file.write(file_data)  # Flush data to master file
                else:
                    print(f"{bmp_file} Hash Mismatch!\nhash_module(temp_data)\nhash_table[f'{file_name_micro}']")
                    sys.exit(1)  # Exit process whenever there is a hash mismatch
                temp_data.close()  # Flush remaining data from memory
        write_clock2: float = now()  # End clock cycle
        print(f"{averages(chunk_size=int(meta['CHUNK']), clock1=write_clock1, clock2=write_clock2)} MB/s AVERAGE WRITE")


def create_meta(file_number: int, file_size: int, hash_table: dict, raw_name: str, chunk_size: int, output_dir: str = _OUTPUT_) -> None:
    """
    :param chunk_size: Size of chunk for file creation
    :param file_number: Number of files/chunks used to make original file
    :param file_size: Original file size in bytes
    :param hash_table: Table of BMP file hashes/chunk hashes
    :param raw_name: The raw file name, such as 'File.fil'
    :param output_dir: User or Default output directory
    :return: None, does not return data, writes to file
    """
    raw_micro: str = raw_name[:-4]  # Raw name excluding file extension
    bmp_name: str = f"{raw_micro}.bmpfile.bmp"  # Name of meta file to create
    meta: dict = {}  # All meta values to be stored as Dict
    with open(f"{output_dir}/{raw_micro}/{bmp_name}", 'wb+') as meta_header:  # Open meta file and write header to it
        meta_header.write(compliant_header)  # Attach header
        meta_header.close()  # Close file for next operation
    with open(f"{output_dir}/{raw_micro}/{bmp_name}", 'a') as meta_data:  # Open meta for string data to be appended
        meta["NAME"]: str = f"{raw_name}"  # File name
        meta["FILES"]: int = int(file_number)  # Number of files
        meta["FILE_SIZE"]: int = int(file_size)  # Size of original file
        meta["HASHES"]: str = f"{hash_table}"  # Table of chunk/BMP hashes
        meta["CHUNK"]: int = int(chunk_size)
        meta["VERSION"]: str = f"{VERSION}"
        meta_data.write("\n")  # Create new line after header
        json.dump(meta, meta_data, indent=3)  # Flush all values to file
        meta_data.close()  # Free up used memory space
    print(f"Meta File: {bmp_name} Created!")


def hash_module(data_chunk: bytes) -> bytes:
    """
    :param data_chunk: Chunk of raw byte data to be operated on
    :return: A hash string of the above data
    """
    return hashlib.sha256(data_chunk).digest()


def parse_meta(meta_file: str) -> dict:
    """
    :param meta_file: Intake meta file
    :return: Return all meta values for later operation
    """
    with open(meta_file, 'rb+') as json_file:  # Read the raw data of the meta files
        blob: list = json_file.readlines()
        json_file.close()
    # if blob[0].strip(b'\n') == compliant_header:  # Check if header at start of file
    with open(meta_file, 'w+') as json_dump:  # Dump the file contents to standard strings without header
        for line in blob[1:]:  # Ensure header is skipped
            json_dump.write(line.decode('utf-8'))  # Make sure the strings are real strings
        json_dump.close()  # Clean up
    # else:
    #     pass
    return json.load(open(meta_file))  # Open and load meta data in json readable state


def make_master(input_dir: str = _INPUT_, output_dir: str = _OUTPUT_) -> None:
    """
    :param input_dir: User or Default Input directory
    :param output_dir: Use or default Output directory
    :return: None, should never return anything, top-most function
    """
    if not exist(input_dir):  # Create the input directory if it does not exist
        os.mkdir(input_dir)
        print("INPUT Created!")
    else:
        pass
    if not exist(output_dir):  # Create the output directory if it does not exist
        os.mkdir(output_dir)
        print("OUTPUT Created!")
    else:
        pass
    bmpfile_items: list = dir_list(f"{input_dir}/*.bmpfile.bmp")  # Check for meta files in Input
    type_list: int = len(bmpfile_items)  # Count meta files
    items: list = dir_list(f"{input_dir}/*.*")  # Check for files in input
    item_number: int = len(items)  # Count files
    if type_list < 1 <= item_number:  # If there are no meta files, proceed as normal
        for item in items:  # Iterate over list of files
            raw_name: str = (((item.replace('\\', '/')).split("/"))[-1])  # Get their raw names
            file_size: int = os.path.getsize(item)  # Get their file sizes
            print(f"Working On: {raw_name}\nFile Size: {file_size}")
            chunk(file_size=file_size, raw_name=raw_name)  # Begin chunking files
            print(f"{raw_name} Complete!\n")
    elif type_list >= 1:  # If there are meta files present, they take priority and will be operated on
        for item in bmpfile_items:  # iterate over list of meta files
            demake_bmpx(meta_file=item)  # Begin rebuild process
    else:
        print("Cannot determine method, lacking data!")


make_master()
