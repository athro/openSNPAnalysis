import csv
import sys
import os.path

debug = True
if debug:
    # andreas is lazy
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pprint = pp.pprint

def incHash(theHash,theKey):
    try:
        theHash[theKey]
    except:
        theHash[theKey] = 0
        pass
    theHash[theKey] += 1
    


def get_vals(pheno_num,pheno_file):
    return_pheno_name = None
    return_pheno_vals = []
    
    with open(pheno_file,  encoding="utf-8") as f:
        r = csv.reader(f,delimiter=';')
        names = next(r)
        if debug:
            print(list(enumerate(map(lambda x: x.encode(), names))))
        # print('Phenotype:%3s:%30s' % (pheno_num, names[pheno_num]))
        print(names[pheno_num]+'\n')
        return_pheno_name = names[pheno_num]
        d = {}
        for row in r:
            d[row[pheno_num].lower()] = 1
        if debug:
            for k in sorted(d.keys()):
                # after having problems with unicode again
                print('%s' % (k.encode(),) + ';')
                # print(k+';')
    
        return_pheno_vals = sorted(d.keys())
        return (return_pheno_name,return_pheno_vals)
    

def write_vals(pheno_name,pheno_vals,mapping_dir):
    mapping_file_name = '%s%s%s' % (mapping_dir,os.path.sep,pheno_name)
    with open(mapping_file_name,  'w', encoding="utf-8") as fh:
        fh.writelines(map(lambda x: '%s;\n' % (x,), pheno_vals))
        fh.close()
    
if __name__ == "__main__":
    data_dir            = '..'+os.path.sep+'..'+os.path.sep+'data' 
    data_dir_genotype   = '%s%sgenotypes' % (data_dir,os.path.sep)
    data_dir_phenotype  = '%s%sphenotypes' % (data_dir,os.path.sep)
    data_dir_annotation = '%s%sannotation' % (data_dir,os.path.sep)
    mapping_dir         = "mapping"

    #pheno_file          = "%s%sphenotypes_201604281702.csv" % (data_dir_phenotype,os.path.sep)
    pheno_file          = "%s%sphenotypes_201604281702.csv.clean.csv" % (data_dir_phenotype,os.path.sep)

    pheno_num = int(sys.argv[1])
    (pheno_name,pheno_vals) = get_vals(pheno_num,pheno_file)
    write_vals(pheno_name,pheno_vals,mapping_dir)
