import csv
import sys
import os.path

import os
import glob
import re
import compress

debug = True

file_re = re.compile('user(\d+)\_file(\d+)\_yearofbirth\_(\w+)\_sex\_(\w+)\.(\S+)\.txt')

def load_mapping(mapping_dir,mapping_name):
    mapping_file = '%s%s%s' % (mapping_dir,os.path.sep,mapping_name)
    mapping = {}
    if os.path.exists(mapping_file):
        with open(mapping_file) as fh:
            mappings_raw = fh.readlines()
        for line in mappings_raw:
            (fromM,toM) = line.strip().split(';')
            mapping[fromM] = toM
    return mapping
        
def snpify_line(a_line,mappings):
    #remove flancking whitepaces
    a_line = a_line.strip()
    #remove overly user of """
    a_line = a_line.replace('"','')

    # do not use empty lines
    if a_line:
    
        # split by using whitespacce
        splitted = a_line.split()
        # try with comma
        if len(splitted)<=1:
            splitted = a_line.split(',')

        # if alleles where one single string
        if len(splitted[-1]) == 2:
            splitted = splitted[:-1]+[splitted[-1][0],splitted[-1][1]]

        # save a lttle bit of length checking
        len_splitted = len(splitted)
        # translate chromosome and print error if chromosome is 0 or something unkown
        chromosome = None 
        if len_splitted >= 4 and len_splitted <= 5:
            try:
                chromosome = mappings['chromosome'][splitted[1]]
            except:
                print('Error on line:\n%s' % (a_line,))
        else:
            print('Problems?: ', splitted)

        snp_data = [splitted[0],chromosome]+splitted[2:]

        return snp_data
    else:
        return None
                

def read_snp_file(file_handle,mappings):
    snp_data = []
    open_possible = False
    with file_handle:
        try:
            data = file_handle.readlines()
        except Exception as e:
        #except:
            print('Could not read in data! Exception: %s' % (e,))
        finally:
            data = []
    for line in data:
        if isinstance(line,(bytes, bytearray)):
            line = line.decode().strip()        
        if not line.startswith('#') and not line.startswith('RSID'):
            snp_line_data = snpify_line(line,mappings)
        if snp_line_data:
            snp_data.append(snp_line_data)
    print('Loaded %s snps' % (len(snp_data),))
    print('-'*80)
    return snp_data
    #file_handle.seek(0)


def read_snps_by_user(userID,data_dir_genotype,mappings):
    if os.path.exists(data_dir_genotype):
        potential_file_names = glob.glob('%s%suser%s_*.txt' % (data_dir_genotype,os.path.sep,userID))
        potential_file_names = [k for k in potential_file_names if not ('vcf.' in k) and not ('.IYG.' in k)]
        if potential_file_names:
            #print(potential_file_names)
            for pot_file in potential_file_names:
                print(pot_file)
                with compress.compress_open(pot_file) as fh:
                    snpData = read_snp_file(fh,mappings)
        else:
            print('No such user=<<%s>>' % (userID,))
                    
    else:
        print('The directory <<%s>> does not exits' % (data_dir_genotype,))
        
    


if __name__ == '__main__':
    data_dir            = '..'+os.path.sep+'..'+os.path.sep+'data'
    data_dir_genotype   = '%s%sgenotypes' % (data_dir,os.path.sep)
    data_dir_phenotype  = '%s%sphenotypes' % (data_dir,os.path.sep)
    data_dir_annotation = '%s%sannotation' % (data_dir,os.path.sep)
    mapping_dir         = "mapping"
    
    example_file1 = '%s%suser972_file483_yearofbirth_unknown_sex_unknown.23andme.txt' % (data_dir_genotype,os.path.sep)
    example_file2 = '%s%suser4468_file3062_yearofbirth_unknown_sex_unknown.ancestry.txt' % (data_dir_genotype,os.path.sep)
    #read_23andme(example_file1)
    # read_ancestry(example_file2)
    mappings = {}
    mappings['chromosome'] = load_mapping(mapping_dir,'chromosome')
    #for i in [125,881,1259]:
    #for i in [1111,850]:
    for i in range(6000):
        read_snps_by_user(i,data_dir_genotype,mappings)

