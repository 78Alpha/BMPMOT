import os
import glob
import sys


def delete(
        root):  # Legacy delete method, use this in a function to automatically delte failed data, if possible, else, remove this
    try:
        os.remove(f"{root}")
        return 0
    except:
        return 1


def chunk(input_dir, output_dir, file_name, file_size, raw_name, chunk_size=48000000):
    """
    :param raw_name:
    :param input_dir: The input_dir in this sense is the file in the input directory rather than the directory itself
    :param output_dir: This is where the data will end up, this value is passed to the bitmap creator function
    :param file_name: The actual file that is being worked on, its name is used for various reasons, from directories to files
    :param file_size: File size is used to determine the number of iterations to run
    :param chunk_size: chunk size is a constant value, this is the amount of data that will be read, but it can be changed depending on target platform
    :var whole_chunks: The number of solid chunks in relation to chunk_size
    :var remainder: If the file is not evenly divisible by whole chunks, it will have its last amount of data read
    :var chunk_data: The actual data in the file, but only a chunk of it to be passed on and processed
    :var core_file: The file to be read in chunks
    :var output_dir_u: Create a directory using the file's name, allow having multiple inputs without crossing images/overwriting data
    :return: Return program status using the C method
    """
    compliant_header = b'BM\xd2\xe4\xde\x02\x00\x00\x00\x00z\x00\x00\x00l\x00\x00\x007\x13\x00\x00\xbf\x0c\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00X\xe4\xde\x02\x13\x0b\x00\x00\x13\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00BGRs\x00\x00\x00\x00\x00\x00'
    assert chunk_size > 0  # chunk size must ALWAYS be greater than zero
    core_file = open(input_dir, 'rb')
    output_dir_u = r"{}{}/".format(output_dir, file_name)
    if not os.path.exists(
            output_dir_u):  # Create the file specific directory if it does not already exist, usually it wont'
        os.mkdir(output_dir_u)
    else:
        pass
    whole_chunks = file_size // chunk_size
    remainder = file_size % chunk_size
    if remainder != 0:
        whole_chunks += 1
    meta_data(raw_name, output_dir_u, compliant_header, whole_chunks)
    for i in range(whole_chunks):
        chunk_data = core_file.read(chunk_size)
        create_bmp(chunk_data, i, output_dir_u, compliant_header, raw_name)


def create_bmp(chunk_data, iteration, output_dir, compliant_header, raw_name):
    """
    :param raw_name:
    :param chunk_data: This is the data in the file, it is read in raw byte format such as \x00, reading file contents normally will not work
    :param iteration: This is the numbered chunk the iterator is currently on, it gives the file its name in relation to position in the file
    :param output_dir: This is the directory where the file is output in its multi-image form
    :param compliant_header: This is the generic header used to create images that are valid across all platforms
    :return: return the status, using the C method of return over python printing errors
    """
    with open("{}/{}.{}.bmp".format(output_dir, raw_name, iteration), "wb+") as bmp_data:
        bmp_data.write(compliant_header)
        bmp_data.write(chunk_data)
        bmp_data.close()
    return 0


def demake_bmp(file_number, input_dir, output_dir, output_name):
    """
    :param output_name: The name of the file to be outputted
    :param input_files: Legacy component with no current use
    :param file_number: number of usable files found in the directory that can be solidified
    :param input_dir: Input_dir in this sense is the actual input directory containing BMP files
    :param output_dir: The directory to output the solid file
    :var new_list: This list contains an ordered list of BMP files from 0 to MAX, this is a lazy method of sorting, used as legacy sort, it works though
    :var temp_data[64:]: This is the data in the file with the header stripped off as to allow it be an actual file again
    :return: Return status in the C method
    """
    new_list = []
    for i in range(file_number):
        new_list.append(f"{input_dir}{output_name}.{i}.bmp")
    master_file = f"{output_dir}{output_name}"
    delete(master_file)
    with open(master_file, 'ab+') as output_file:
        for bmp_file in new_list:
            temp_data = open(bmp_file, 'rb').read()
            output_file.write(temp_data[64:])


def meta_data(file_name, output_dir, header, file_number):
    """
    :param file_name: The name of the file being consolidated
    :param output_dir: The directory to contain the meta file
    :param header: The generic header used to create meta header
    :param file_number: number of bmp files used to make a certain file
    :return: Return status in C method
    """
    bmp_name = f"{file_name}.bmpfile.bmp"
    full_dir = f"{output_dir}/{bmp_name}"
    with open(full_dir, 'wb+') as meta_file:
        meta_file.write(header)
        meta_file.close()
    with open(full_dir, 'a') as meta_file:
        meta_file.write("\n")
        meta_file.write(f"NAME:{file_name}\n")
        meta_file.write(f"FILES:{file_number}\n")


def read_meta(meta_file):
    """
    :param meta_file: The file containing the meta data for end file
    :return: Return the name to be used
    """
    with open(meta_file, 'r') as meta_header:
        data = meta_header.readlines()
        meta_header.close()
    for line in data:
        if "NAME:" in line:
            return line.split("NAME:")[-1]


def make_master():
    """
    :var cwd: The current directory of the file or program
    :var input_dir: The directory used for file input
    :var output_dir: The directory to contain custom outputs
    :var file_number: Lists the number of files in the input directory, if it's more than one, it will assume the directory contains BMP, may be changed in the future, as this is legacy
    :var file_name: The name of the actual file itself, without extension
    :var file_size: The size of the solid file, does not apply to BMP files
    :var type_list: Determine the method to use checking if a meta file exists
    :var functional: The number of iterations to run when remaking the file, error correction for meta included
    :var input_files: The number of files to run iterations without correction for meta file
    :return:
    """
    cwd = os.getcwd()
    input_dir = "{}/Input/".format(cwd)
    output_dir = "{}/Output/".format(cwd)
    file_number = len(glob.glob(f"{input_dir}/*.*"))

    if not os.path.exists(input_dir):  # Create the input directory if it does not exist
        os.mkdir(input_dir)
    else:
        pass
    if not os.path.exists(output_dir):  # Create the output directory if it does not exist
        os.mkdir(output_dir)
        sys.exit()
    else:
        pass
    type_list = len(glob.glob(f"{input_dir}/*.bmpfile.bmp"))
    item_number = len(glob.glob(f"{input_dir}/*.*"))
    if type_list < 1:
        if item_number >= 1:
            items = glob.glob(f"{input_dir}/*.*")
            for item in items:
                print(item)
                input_file = item
                file_name = (((input_file.split("/"))[-1]).split("."))[0]
                raw_name = ((input_file.split("/"))[-1])
                file_size = os.path.getsize(input_file)
                chunk(input_file, output_dir, file_name, file_size, raw_name)
        else:
            print("Error with recursive build!")
    elif type_list >= 1:
        items = glob.glob(f"{input_dir}/*.bmpfile.bmp")
        for item in items:
            output_name = ((item).split(".bmpfile.bmp"))[0].split("/")[-1]
            input_files = glob.glob(f"{input_dir}/{output_name}*.bmp")
            functional = len(input_files) - 1
            demake_bmp(functional, input_dir, output_dir, output_name)
    else:
        print("Cannot determine method, lacking data!")


make_master()
