import gzip
import zipfile
import os

magic = {}
magic["zip"] = b'\x50\x4b\x03\x04'
magic["gzip"] = b'\x1f\x8b\x08'
#magic["bzip"] = b'\x42\x5a\x68'


def open_zip(filename):
    zf = zipfile.ZipFile(filename)
    filenames = zf.namelist()
    fh = zf.open(filenames[0])
    return fh

def open_gzip(filename):
    fh = gzip.GzipFile(filename)
    return fh

get_fh = {}
get_fh["zip"] = open_zip
get_fh["gzip"] = open_gzip
get_fh["plain"] = open


def compress_open(filename):
    with open(filename, 'rb') as f:
        start_of_file = f.read(1024)
    for (kind, bytes) in magic.items():
        if start_of_file.startswith(bytes):
            return get_fh[kind](filename)
    return open(filename)

get_fh = {}
get_fh["zip"] = open_zip
get_fh["gzip"] = open_gzip
get_fh["plain"] = open


if __name__ == "__main__":
    directory = '../../data/genotypes/'
    files = os.listdir(directory)
    for filename in files:
        try:
            cf = compress_open(directory+"/"+filename)
        except:
            print("Can't uncompress "+filename)
