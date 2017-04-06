import gzip
import zipfile
import os
#AK:TBD:# xls unfinished and untested
#AK:TBD:import xlrd

magic = {}
magic["zip"] = b'\x50\x4b\x03\x04'
magic["gzip"] = b'\x1f\x8b\x08'
#magic["bzip"] = b'\x42\x5a\x68'
#AK:TBD:magic["xls"] = b'\xd0\xcf'


#AK:TBD:# change to filehanle for zipped xls?
#AK:TBD:def test_xsl(filename):
#AK:TBD:    with open(filename, 'rb') as f:
#AK:TBD:        buffer = f.read(1024)
#AK:TBD:    return_val = False
#AK:TBD:    if buffer.startswith(magic["xls"]):
#AK:TBD:        return_val = True
#AK:TBD:    return return_val
        

#AK:TBD:# Idea: open xls, convert it to temp. csv, return filehandle for csv
#AK:TBD:def open_xls(filename):
#AK:TBD:    wb = xlrd.open_workbook(filename_temp)
#AK:TBD:    ws = wb.sheets()[0]
#AK:TBD:    temp_csv_file_name = get_temp_csv_file_name
#AK:TBD:    temp_csv_file = open(temp_csv_file_name, 'wb')
#AK:TBD:    wr = csv.writer(temp_csv_file, quoting=csv.QUOTE_ALL)
#AK:TBD:    for rownum in xrange(ws.nrows):
#AK:TBD:        wr.writerow(ws.row_values(rownum))
#AK:TBD:    temp_csv_file.close()

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
#AK:TBD:get_fh["xls"] = open_xls
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
#AK:TBD:get_fh["xls"] = open_xls
get_fh["plain"] = open


if __name__ == "__main__":
    directory = '../../data/genotypes/'
    files = os.listdir(directory)
    for filename in files:
        try:
            cf = compress_open(directory+"/"+filename)
        except:
            print("Can't uncompress "+filename)
