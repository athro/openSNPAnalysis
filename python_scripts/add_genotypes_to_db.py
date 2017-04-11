import sys
import os.path
#import getopt
import pymysql
import csv
#import traceback
import db_utils
import utils

import read_genotypes
 
debug = True

# insert_user_query        = "insert into user (id) values (%s)"
# insert_pheno_name_query  = "insert into phenotype (name) values (%s)"
# insert_pheno_value_query = "insert into phenotype_value (id_pheno, value) values (%s, %s)"
# insert_pheno_user_query  = "insert into pheno_user (id_pheno, id_user, id_phenotype_value) values (%s, %s, %s)"
# select_pheno_val_query   = "select id from phenotype_value where id_pheno = %s and value = %s"
# select_user_query        = "select id from user where id = %s"

select_all_snps_query      = "select id,name,chromosome,location from snp"
select_snp_query_by_name   = "select id,name,chromosome,location from snp where name = %s"
select_snp_query_by_id     = "select id,name,chromosome,location from snp where id = %s"
insert_into_snp_query      = "insert into snp (name,chromosome,location) values (%s,%s,%s)"

select_all_alleles_query    = "select id,allele1,allele2 from allele"
insert_into_allele_query    = "insert into allele (allele1,allele2) values (%s,%s)"


snps = {}


def db_connect():
    db_params = db_utils.get_db_params()
    print(db_params)
    try:
        db_connection = pymysql.connect( host   = db_params['hostname'],
                              db     = db_params['dbname'],
                              user   = db_params['username'],
                              passwd = db_params['pword'],
                              charset= 'utf8')
    except pymysql.MySQLError:
        sys.stderr.write("Failed to connect to database: " + db_params['dbname'] + " on " + db_params['hostname'] + "\n")
        sys.exit(1)
    return db_connection

def set_up_snps_from_db(db_connection):
    snp_hash = {}
    result = db_utils.db_select_all(db_connection, select_all_snps_query)
    if not result:
        False
    else:
        for (id,name,chromosome,location) in result:
            snp_hash[name] = id
    return snp_hash

def set_up_alleles_from_db(db_connection):
    allele_hash = {}
    result = db_utils.db_select_all(db_connection, select_all_alleles_query)
    if not result:
        False
    else:
        for (id,allele1,allele2) in result:
            utils.insert_double_key_hash(allele_hash,allele1,allele2,id)
    return allele_hash

def get_info(snp_info):
    used_snps     = {}
    used_alleles  = {}
    for entry in snp_info[:10]:
        print(entry)
    return (used_snps,used_alleles)

def insert_new_alleles_into_db(db_connection,hash_allele,hash_allele_temp):
    for allele1 in hash_allele_temp.keys():
        for allele2 in hash_allele_temp[allele1].keys():
            db_id = db_utils.db_insert_auto_id(db_connection, insert_into_allele_query, (allele1,allele2))
            utils.insert_double_key_hash(hash_allele,allele1,allele2,db_id)
            print('insert: ',allele1,allele2,db_id)


def check_snp_file_entries(genotype_data,hash_snp,hash_allele):
    hash_snp_temp = {}
    hash_allele_temp = {}
    
    for genotype_entry in genotype_data:
        name_snp    = genotype_entry[0]
        allele1_snp = genotype_entry[3]
        allele2_snp = '#' # only one single character possible. # indicates None
        if len(genotype_entry) == 5:
            allele2_snp = genotype_entry[4]

        if name_snp not in hash_snp:
            if name_snp not in hash_snp_temp:
                hash_snp_temp[name_snp] = {}
        if not utils.has_double_key_hash(hash_allele,allele1_snp,allele2_snp):
            if not utils.has_double_key_hash(hash_allele_temp,allele1_snp,allele2_snp):
                utils.insert_double_key_hash(hash_allele_temp,allele1_snp,allele2_snp,None)
    return (hash_snp_temp,hash_allele_temp)    
    
if __name__ == '__main__':
    data_dir            = '..'+os.path.sep+'..'+os.path.sep+'data'
    data_dir_genotype   = '%s%sgenotypes' % (data_dir,os.path.sep)
    data_dir_phenotype  = '%s%sphenotypes' % (data_dir,os.path.sep)
    data_dir_annotation = '%s%sannotation' % (data_dir,os.path.sep)
    mapping_dir         = "mapping"

    # load chromosome mappings
    mappings = {}
    mappings['chromosome'] = read_genotypes.load_mapping(mapping_dir,'chromosome')

    # get db connection    
    db_connection = db_connect()
    hash_allele = set_up_alleles_from_db(db_connection)
    print('hash_allele',hash_allele)

    hash_snp = set_up_snps_from_db(db_connection)
    print('hash_snp',hash_snp)

    for i in range(2,170):
    #for i in [885,]: # quick alternative: 937
         genotype_data = read_genotypes.read_snps_by_user(i,data_dir_genotype,mappings)
         print(len(genotype_data))
         (hash_snp_temp,hash_allele_temp) = check_snp_file_entries(genotype_data,hash_snp,hash_allele)
         insert_new_alleles_into_db(db_connection,hash_allele,hash_allele_temp)
