import matplotlib.pyplot as plt
import csv
import sys
import os.path

debug = True

min_thresh = 250
label_length = 35

def read_pheno(filename):
    results = {}
    with open(filename, encoding="utf-8") as f:
        r = csv.reader(f, delimiter=';')
        # header line holds the phenotype names
        names = next(r)
        for name in names:
            results[name] = []
        # now for the data
        for row in r:
            for (phenonum,name) in enumerate(names[1:],start=1):
                if row[phenonum] != "-":
                    results[name].append(row[phenonum].lower())
    # remove any that are too few
    to_remove = [k for k, v in results.items() if len(v) < min_thresh]
    for name in to_remove:
        del results[name]
    return results

def plot_bar(name, vals, outdir):
    d = {}
    # count how many of each value
    for p in vals:
        d[p] = d.get(p,0) + 1
    items = sorted(d.items(), reverse=True) # alphabetic by phenotype name
    num_items = len(items)
    yvals = [i[1] for i in items]
    labels = [i[0][:label_length] for i in items]
    nums = range(num_items)

    plt.barh(nums, yvals, align='center')
    plt.yticks(nums, labels)
    plt.ylim(-1, num_items)
    plt.tight_layout()
    plt.title(name)
    #plt.show()
    plt.savefig(outdir + name.replace(" ","_") + ".png", bbox_inches='tight')
    plt.close()
            

if __name__ == "__main__":
    data_dir            = '..'+os.path.sep+'..'+os.path.sep+'data' 
    data_dir_genotype   = '%s%sgenotypes' % (data_dir,os.path.sep)
    data_dir_phenotype  = '%s%sphenotypes' % (data_dir,os.path.sep)
    data_dir_annotation = '%s%sannotation' % (data_dir,os.path.sep)
    data_file           = 'phenotypes_201604281702.csv.clean.csv'

    outdir = '..'+os.path.sep+'..'+os.path.sep+'results'+os.path.sep
    print ("%s%s%s" % (data_dir_phenotype,os.path.sep,data_file))
    data = read_pheno("%s%s%s" % (data_dir_phenotype,os.path.sep,data_file))
    for name, vals in data.items():
        if debug:
            print('Processing <<%s>>' % (name))
        plot_bar(name, vals, outdir)

