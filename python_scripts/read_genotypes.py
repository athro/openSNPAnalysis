import csv
import sys
import os.path

import os
import glob
import re
import compress
import zipfile

import add_genotypes_to_db as db_geno

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
    """Returns a SNP data dictionary of id, chromosome, loc and allele vals, or returns None"""
    # remove flanking whitepaces
    a_line = a_line.strip()
    # remove over use of """
    a_line = a_line.replace('"','')

    # do not use empty lines
    if a_line:
    
        # split by using whitespacce
        splitted = a_line.split()
        # try with comma
        if len(splitted)<=1:
            splitted = a_line.split(',')

        # if alleles were one single string
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
                sys.stderr.write('Error on line: %s\n' % (a_line,))
                pass
        else:
            sys.stderr.write('Problems?: ', splitted)
            sys.stderr.write('\n')

        snp_data = { 'snp_id':splitted[0],
                     'chromosome':chromosome,
                     'location':splitted[2],
                     'allele1':splitted[3] }
        if len_splitted > 4:
            snp_data['allele2'] = splitted[4]

        return snp_data
    else:
        return None
                

def read_snp_file(file_handle,mappings):
    """Returns a list of SNP data dicts"""
    snp_data = []
    open_possible = False
    with file_handle:
        try:
            data = file_handle.readlines()
        except Exception as e:
            sys.stderr.write('Could not read in data! Exception: %s\n' % (e,))
            data = []
    for line in data:
        if isinstance(line,(bytes, bytearray)):
            line = line.decode().strip()        
        if not line.startswith('#') and not line.startswith('RSID'):
            snp_line_data = snpify_line(line,mappings)
            # check if data (location) is actually set
            if snp_line_data and snp_line_data['chromosome'] and snp_line_data['location']:
                snp_data.append(snp_line_data)
    print('Loaded %s snps' % (len(snp_data),))
    print('-'*80)
    return snp_data
    #file_handle.seek(0)


def read_snps_by_user(user_id, data_dir_genotype, mappings):
    """Returns a list of (filename,method,snp_data) triples.
    A user may have multiple files.
    The snp_data is a list of dicts.
    """
    return_values = []
    if os.path.exists(data_dir_genotype):
        potential_file_names = glob.glob('%s%suser%s_*.txt' % (data_dir_genotype, os.path.sep, user_id))
        potential_file_names = [k for k in potential_file_names if not ('vcf.' in k) and not ('.IYG.' in k)]
        if potential_file_names:
            #print(potential_file_names)
            for pot_file in potential_file_names:
                #print(pot_file)
                try:
                    with compress.compress_open(pot_file) as fh:
                        snp_data = read_snp_file(fh, mappings)
                except zipfile.BadZipFile as e:
                    sys.stderr.write('Bad ZIP File - contents ignored (<<%s>>)\n' % (pot_file,))
                else:
                    method = pot_file.split('.')[-2] # From filename. But can we determine this?
                    return_values.append((pot_file, method, snp_data))   
        else:
            sys.stderr.write('No input file for user=<<%s>>\n' % (user_id,))
                    
    else:
        sys.stderr.write('The directory <<%s>> does not exist\n' % (data_dir_genotype,))
        
    return return_values


if __name__ == '__main__':
    data_dir            = '..'+os.path.sep+'..'+os.path.sep+'data'
    data_dir_genotype   = '%s%sgenotypes' % (data_dir,os.path.sep)
    data_dir_phenotype  = '%s%sphenotypes' % (data_dir,os.path.sep)
    data_dir_annotation = '%s%sannotation' % (data_dir,os.path.sep)
    mapping_dir         = "mapping"
    
    #example_file1 = '%s%suser972_file483_yearofbirth_unknown_sex_unknown.23andme.txt' % (data_dir_genotype,os.path.sep)
    #example_file2 = '%s%suser4468_file3062_yearofbirth_unknown_sex_unknown.ancestry.txt' % (data_dir_genotype,os.path.sep)
    #read_23andme(example_file1)
    # read_ancestry(example_file2)
    mappings = {}
    mappings['chromosome'] = load_mapping(mapping_dir, 'chromosome')
    # test special
    #for i in [1497,125,881,1259,1111,850]:
    # test all
    #for i in range(6000):
    # test not tested yet
    #for i in range(2198,6000):
    for i in [77,]:
        snp_data = read_snps_by_user(i, data_dir_genotype, mappings)
        if snp_data:
            for (filename, method, genotype) in snp_data:
                print(filename, method, len(genotype))
