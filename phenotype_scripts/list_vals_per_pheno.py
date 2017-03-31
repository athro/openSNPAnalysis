import csv
import sys

def get_vals(pheno_num,pheno_file):
    with open(pheno_file) as f:
        r = csv.reader(f,delimiter=';')
        names = next(r)
        print(list(enumerate(names)))
        print(names[pheno_num] + "\n")
        d = {}
        for row in r:
            d[row[pheno_num].lower()] = 1
        for k in sorted(d.keys()):
            print(k + ';')
        
    

if __name__ == "__main__":
    pheno_file = "../data/phenotypes/phenotypes_201604281702.csv"
    pheno_num = int(sys.argv[1])
    get_vals(pheno_num,pheno_file)
    
