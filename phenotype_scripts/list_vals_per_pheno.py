import csv
import sys
import os.path

debug = False

def incHash(theHash,theKey):
    try:
        theHash[theKey]
    except:
        theHash[theKey] = 0
        pass
    theHash[theKey] += 1
    


def get_vals(pheno_num,pheno_file):
    with open(pheno_file,  encoding="utf-8") as f:
        r = csv.reader(f,delimiter=';')
        names = next(r)
        if debug:
            print(list(enumerate(map(lambda x: x.encode(), names))))
        # print('Phenotype:%3s:%30s' % (pheno_num, names[pheno_num]))
        print(names[pheno_num]+'\n')
        d = {}
        # ak: for later
        count = {}

        # back to original:
        for row in r:
            d[row[pheno_num].lower()] = 1
            incHash(count,row[pheno_num].lower())
        for k in sorted(d.keys()):
            # after having problems with unicode again
            print('%s' % (k.encode(),) + ';')

        # # why not:
        # # without count
        # print(';\n'.join(sorted(count.keys())))
        # # with count
        # print(';\n'.join(map(lambda x: '%s:%s' % (x[0].encode(),x[1]),sorted(zip(count.keys(),count.values())))))
        # # is that bad style because of map and lambda?
        
    

if __name__ == "__main__":
    data_dir            = '..'+os.path.sep+'..'+os.path.sep+'data' 
    data_dir_genotype   = '%s%sgenotypes' % (data_dir,os.path.sep)
    data_dir_phenotype  = '%s%sphenotypes' % (data_dir,os.path.sep)
    data_dir_annotation = '%s%sannotation' % (data_dir,os.path.sep)

    #pheno_file          = "%s%sphenotypes_201604281702.csv" % (data_dir_phenotype,os.path.sep)
    pheno_file          = "%s%sphenotypes_201604281702.csv.clean.csv" % (data_dir_phenotype,os.path.sep)

    pheno_num = int(sys.argv[1])
    get_vals(pheno_num,pheno_file)
    
