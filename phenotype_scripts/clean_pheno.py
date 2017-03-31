import csv
import os


def read_mapping_files(mapping_dir, mapping_files):
    mapping = {}
    for name in mapping_files:
        mapping[name] = {}
        with open(mapping_dir+"/"+name) as f:
            mapping[name]['-'] = '-'
            for line in f:
                [old,new] = line.strip().split(';',2)
                mapping[name][old] = new
    return mapping


def clean_phenos(pheno_file, mapping):
    with open(pheno_file) as f, open(pheno_file+".clean.csv","w") as fo:
        r = csv.reader(f, delimiter=';')
        w = csv.writer(fo, delimiter=';')
        # header line holds the phenotype names
        names = next(r)
        w.writerow(names)

        for row in r:
            out = []
            for n,v in zip(names, row):
                if n in mapping:
                    out.append(mapping[n][v.lower()])
                else:
                    out.append(v.lower())
            w.writerow(out)

            
if __name__ == "__main__":
    mapping_dir = "mapping"
    pheno_file = "../data/phenotypes/phenotypes_201604281702.csv"
    mapping = read_mapping_files(mapping_dir, os.listdir(mapping_dir))
    clean_phenos(pheno_file, mapping)
