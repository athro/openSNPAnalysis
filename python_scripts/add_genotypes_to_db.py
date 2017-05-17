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


select_all_snps_query      = "select id,name,chromosome,location from snp"
select_snp_query_by_name   = "select id,name,chromosome,location from snp where name = %s"
select_snp_query_by_id     = "select id,name,chromosome,location from snp where id = %s"
insert_into_snp_query      = "insert into snp (name,chromosome,location) values (%s,%s,%s)"

select_all_alleles_query   = "select id,allele1,allele2 from allele"
insert_into_allele_query   = "insert into allele (allele1,allele2) values (%s,%s)"

select_user_query          = "select id from user where id = %s"
insert_user_query          = "insert into user (id) values (%s)"

select_all_methods_query   = "select id, name from geno_method"
insert_geno_method_query   = "insert into geno_method (name) values (%s)"
insert_geno_file           = "insert into genotype_file (filename, id_user, id_method) values (%s, %s, %s)"

snps = {}


def db_connect():
    db_params = db_utils.get_db_params_from_config()
    print(db_params['hostname'])
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
    for (id,name,chromosome,location) in result:
        snp_hash[name] = id
    return snp_hash

def set_up_alleles_from_db(db_connection):
    allele_hash = {}
    result = db_utils.db_select_all(db_connection, select_all_alleles_query)
    for (id,allele1,allele2) in result:
        utils.insert_double_key_hash(allele_hash,allele1,allele2,id)
    return allele_hash

def set_up_geno_methods_from_db(db_connection):
    method_hash = {}
    result = db_utils.db_select_all(db_connection, select_all_methods_query)
    if not result:
        methods = ['23andme','23andme-exome-vcf','IYG','ancestry','csv','decodeme','ftdna-illumina']
        (start,end) = db_utils.db_insert_auto_id_bulk(db_connection, insert_geno_method_query, methods)
        method_hash = dict(zip(methods, range(start,end+1)))
    else:
        for (id, name) in result:
            method_hash[name] = id
    return method_hash
            

# what was this function?
def get_info(snp_info):
    used_snps     = {}
    used_alleles  = {}
    for entry in snp_info[:10]:
        print(entry)
    return (used_snps,used_alleles)

def insert_new_alleles_into_db(db_connection, hash_allele, hash_allele_temp):
    """Inserts into database and also modifies hash_allele to add contents of hash_allele_temp with new db ids"""
    for allele1 in hash_allele_temp.keys():
        for allele2 in hash_allele_temp[allele1].keys():
            db_id = db_utils.db_insert_auto_id(db_connection, insert_into_allele_query, (allele1,allele2))
            utils.insert_double_key_hash(hash_allele,allele1,allele2,db_id)
            print('insert: ',allele1,allele2,db_id)
    return hash_allele

def insert_genotype_file(db_connection, filename, user_id, method_id):
    db_id = db_utils.db_insert_auto_id(db_connection, insert_geno_file, (filename, user_id, method_id))
    return db_id

#not yet written
def insert_new_genotypes_into_db(db_connection, hash_snp, hash_snp_temp):
    """Inserts into database and also modifies hash_snp to add contents of hash_snp_temp with new db ids"""
    for name_snp in hash_snp_temp.keys():
        db_id = db_utils.db_insert_auto_id(db_connection, insert_into_snp_query, (name, chromosome, location))
        # need to update the hash

    return hash_snp

def check_or_insert_user(db_connection, user_id):
    res = db_utils.db_select_one(db_connection, select_user_query, (user_id,))
    if res == None:
        db_utils.db_insert_no_auto_id(db_connection, insert_user_id, (user_id,))


def check_snp_file_entries(genotype_data,hash_snp,hash_allele):
    """
    If any snps are not already in the db, we save them into a temporary hash for later batch deposit.
    Parameters:
    genotype_data is a list of dictionaries, one per SNP
    hash_snp is a hash of name->id mappings for SNPs in the db
    hash_allele is a hash of allele1->allele2->id mappings for alleles in the db 
    Returns:
    the constructed pair of temporary hashes
    """
    hash_snp_temp = {}
    hash_allele_temp = {}
    
    for genotype_entry in genotype_data:
        name_snp    = genotype_entry['snp_id']
        allele1_snp = genotype_entry['allele1']
        allele2_snp = genotype_entry.get('allele2') # default None if not found 

        if name_snp not in hash_snp:
            if name_snp not in hash_snp_temp:
                hash_snp_temp[name_snp] = {}
        if not utils.has_double_key_hash(hash_allele, allele1_snp, allele2_snp):
            if not utils.has_double_key_hash(hash_allele_temp, allele1_snp, allele2_snp):
                utils.insert_double_key_hash(hash_allele_temp, allele1_snp, allele2_snp, None)
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
    hash_method = set_up_geno_methods_from_db(db_connection)
    
    #for i in range(2,170):
    for user_id in [881,]: # 885, quick alternative: 937
        check_or_insert_user(db_connection, user_id)
        snp_data = read_genotypes.read_snps_by_user(user_id, data_dir_genotype, mappings)
        for (filename, method, genotype_data) in snp_data:
            print(filename, method, len(genotype_data))
            (hash_snp_temp, hash_allele_temp) = check_snp_file_entries(genotype_data, hash_snp, hash_allele)
            hash_allele = insert_new_alleles_into_db(db_connection, hash_allele, hash_allele_temp)
            
            # assumption! that method is in the db and therefore in the hash! but there are very few methods so more efficient to assume.
            file_id = insert_genotype_file(db_connection, filename, user_id, hash_method[method])
            print("file_id", file_id)

            # add or check the snp (name, chromosome, location)
            # hash_snp = insert_new_snps_into_db(db_connection, genotype_data, hash_snp, hash_snp_temp)

            # add the genotype : snp_id, allele_id, file_id
