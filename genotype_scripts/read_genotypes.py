import csv
import sys
import os.path

debug = True

def read_23andme(file_name):
    ret_val = None
    if os.path.exists(file_name):
        with open(file_name, 'r') as fh:
            r = csv.reader((row for row in fh if not row.startswith('#')),delimiter='\t')
            ret_val = map(lambda x: x[:-1]+list(x[-1])+[x],list(r))
            # may be wrong number of arguments?

            not_matching = filter(lambda x: len(x) != 6, ret_val)
            if not_matching:
                print('Error in file <<%s>>' % (file_name,))
                if debug:
                    print('lenerrors   = %s' % (len(not_matching)))
                    print('lenerrors[:10] = %s' % (not_matching[:10]))
            
        fh.close()
        if debug:
            print('The 10 of %s first entries in <<%s>> are:' % (len(ret_val),file_name))
            print(ret_val[:10])

    else:
        print('The file <<%s>> does not exits' % (file_name,))
    return ret_val


if __name__ == '__main__':
    data_dir            = '..'+os.path.sep+'..'+os.path.sep+'data'
    data_dir_genotype   = '%s%sgenotypes' % (data_dir,os.path.sep)
    data_dir_phenotype  = '%s%sphenotypes' % (data_dir,os.path.sep)
    data_dir_annotation = '%s%sannotation' % (data_dir,os.path.sep)

    example_file = '%s%suser972_file483_yearofbirth_unknown_sex_unknown.23andme.txt' % (data_dir_genotype,os.path.sep)
    
    read_23andme(example_file)
