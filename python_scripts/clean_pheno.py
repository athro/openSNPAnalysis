import csv
import os
import os.path

debug = True

def read_mapping_files(mapping_dir):
    mapping_files = os.listdir(mapping_dir)
    mapping = {}
    for name in mapping_files:
        mapping[name] = {}
        with open(mapping_dir+"/"+name, encoding='utf-8') as f:
            mapping[name]['-'] = '-'
            r = csv.reader(f,delimiter=';')
            for row in r:
                [old, new] = row
                # get rid of tabs etc within the values
                old = ' '.join(old.strip().split())
                new = ' '.join(new.strip().split())
                mapping[name][old] = new
    return mapping


def clean_phenos(pheno_file, mapping):
    cleaned_pheno_file = '%s.clean.csv' % (pheno_file)
    with open(pheno_file, encoding="utf-8") as f, open(cleaned_pheno_file,"w", encoding="utf-8") as fo:
        r = csv.reader(f, delimiter=';')
        w = csv.writer(fo, delimiter=';')
        # header line holds the phenotype names
        names = next(r)
        w.writerow(names)

        for row in r:
            out = []
            for n,v in zip(names, row):
                v = ' '.join(v.strip().split()).lower()
                if n in mapping:
                    out.append(mapping[n][v])
                else:
                    out.append(v)
            w.writerow(out)

    if debug:
        print('Saved cleaned phenotypes in file <<%s>>' % (cleaned_pheno_file,))
            
if __name__ == "__main__":
    data_dir            = '../../data/'
    data_dir_genotype   = '%s%sgenotypes' % (data_dir,os.path.sep)
    data_dir_phenotype  = '%s%sphenotypes' % (data_dir,os.path.sep)
    data_dir_annotation = '%s%sannotation' % (data_dir,os.path.sep)
    
    mapping_dir         = "mapping"
    pheno_file          = "%s%sphenotypes_201604281702.csv" % (data_dir_phenotype,os.path.sep)

    mapping = read_mapping_files(mapping_dir)
    clean_phenos(pheno_file, mapping)
