import logging
import logger
logger_instance = logger.setup_logger('openSNPAnalysis','openSNPAnalysis.log',logging.DEBUG)

import sys
import os.path
#import getopt
import pymysql
import csv
#import traceback
import db_utils
import utils

import read_genotypes


select_all_snps_query      = "select id,name,chromosome,location from snp"
select_snp_query_by_name   = "select id,name,chromosome,location from snp where name = %s"
select_many_snp_query_by_name   = "select name,id from snp where name in (%s)" # for hash look up
select_snp_query_by_id     = "select id,name,chromosome,location from snp where id = %s"
insert_into_snp_query      = "insert into snp (name,chromosome,location) values (%s,%s,%s)"

select_all_alleles_query   = "select id,allele1,allele2 from allele"
insert_into_allele_query   = "insert into allele (allele1,allele2) values (%s,%s)"

select_user_query          = "select id from user where id = %s"
insert_user_query          = "insert into user (id) values (%s)"

select_all_methods_query   = "select id, name from geno_method"
insert_geno_method_query   = "insert into geno_method (name) values (%s)"
select_filename_query      = "select id from genotype_file where filename = %s"
insert_geno_file           = "insert into genotype_file (filename, id_user, id_method) values (%s, %s, %s)"

insert_genotype_query      = "insert into genotype (id_snp, id_allele, id_genotype_file) values (%s, %s, %s)"

snps = {}




def db_connect():
    db_params = db_utils.get_db_params_from_config()
    logger_instance.info('Connecting to host: %s' % (db_params['hostname'],))
    try:
        db_connection = pymysql.connect( host   = db_params['hostname'],
                              db     = db_params['dbname'],
                              user   = db_params['username'],
                              passwd = db_params['pword'],
                              charset= 'utf8')
    except pymysql.MySQLError:
        err_string = "Failed to connect to database: " + db_params['dbname'] + " on " + db_params['hostname']
        sys.stderr.write(err_string + "\n")
        logger_instance.debug(err_string)
        sys.exit(1)
    return db_connection

# -----------------------------------------------------------------------------------
# Cache ids from certain db tables in memory in dicts (snps, alleles, geno_methods)

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
            

# -----------------------------------------------------------------------------------


# what was this function?
def get_info(snp_info):
    logger_instance.debug('snp_info:      %s' % (snp_info,))
    used_snps     = {}
    used_alleles  = {}
    for entry in snp_info[:10]:
        print(entry)
    return (used_snps,used_alleles)

# ----------------------------------------------------------------------------------
# Database inserts

def insert_new_alleles_into_db(db_connection, hash_allele, hash_allele_temp):
    logger_instance.debug('len(hash_allele):      %s' % (len(hash_allele),))
    logger_instance.debug('len(hash_allele_temp): %s' % (len(hash_allele_temp),))
    """Inserts into database and also modifies hash_allele to add contents of hash_allele_temp with new db ids"""
    for allele1 in hash_allele_temp.keys():
        for allele2 in hash_allele_temp[allele1].keys():
            db_id = db_utils.db_insert_auto_id(db_connection, insert_into_allele_query, (allele1,allele2))
            utils.insert_double_key_hash(hash_allele,allele1,allele2,db_id)
            # print('insert: ',allele1,allele2,db_id)
    return hash_allele

def select_or_insert_genotype_file(db_connection, filename, user_id, method_id):
    logger_instance.debug('filename:     %s' % (filename,))
    file_id = None
    result = db_utils.db_select_one(db_connection, select_filename_query, (filename,))
    if not result:
        file_id = db_utils.db_insert_auto_id(db_connection, insert_geno_file, (filename, user_id, method_id))
    else:
        file_id = result[0]
    return file_id

def insert_new_snps_into_db(db_connection, hash_snp, hash_snp_temp):
    """Inserts into database and also modifies hash_snp to add contents of hash_snp_temp with new db ids"""
    logger_instance.debug('len(hash_snp.keys()):   %s' % (len(hash_snp.keys()),))

    # for checking later:
    number_keys_in_hash_before = len(hash_snp.keys())
    
    # for name_snp in hash_snp_temp.keys():
    #     (chromosome, location) = hash_snp_temp[name_snp]
    #     #AK: not bulk!
    #     db_id = db_utils.db_insert_auto_id(db_connection, insert_into_snp_query, (name_snp, chromosome, location))
    #     #AK: not bulk!
    #     # update the hash_snp with the new id
    #     hash_snp[name_snp] = db_id
    # bulkify

    # extract the required data
    chromo_loc_data = [(name_snp, hash_snp_temp[name_snp][0], hash_snp_temp[name_snp][1]) for name_snp in hash_snp_temp.keys()]

    # insert as bulk, return values are begin and end of the auto IDs
    (db_ids_start,db_ids_end) = db_utils.db_insert_auto_id_bulk(db_connection, insert_into_snp_query, chromo_loc_data)
     
    # convert these IDs to a list, just to zip it later for inserting into hash_snp
    logger_instance.debug('Return Values IDs:       %s' % ((db_ids_start,db_ids_end),))

    # do a sanity check (i.e. check if the length of the tuples to be inserted is the same as the returned IDs):
    if len(hash_snp_temp.keys()) != db_ids_end-db_ids_start+1:
        err_string = 'Bulk insert for SNPs returned a different number of IDs (#Keys SNPs:%s =/= #IDs:%s)' % (len(hash_snp_temp.keys()),len(db_ids))
        logger_instance.debug(err_string)
        logger_instance.error(err_string)
        sys.exit(-1)

    # insert the IDs in the corresponding hash
    # the return values from_bulk are not really reliable: problem between different tables and the function LAST_INSERT_ID()
    # therefore: select and fill the corresponding data

    #if hash_snp_temp not empty
    if len(hash_snp_temp.keys())>0:
        # construct variable number of %s
        variable_number_of_format_strings = ','.join(['%s'] * len(hash_snp_temp.keys()))
        # logger_instance.debug('variable_number_of_format_strings = %s' % (variable_number_of_format_strings))
        select_statement = select_many_snp_query_by_name % (variable_number_of_format_strings,)
        # logger_instance.debug('select_statement = %s' % (select_statement,))
        returnedIDs = db_utils.db_select_all(db_connection,select_statement,[(x,) for x in hash_snp_temp.keys()])
        # logger_instance.debug(returnedIDs)
        # sys.exit(-2)
    
        for (name_snp,db_id) in returnedIDs:
            #just_blocks_the_logger:  logger_instance.debug('name_snp = %15s : db_id = %10s' % (name_snp,db_id,))
            hash_snp[name_snp] = db_id

    number_keys_in_temphash = len(hash_snp_temp.keys())
    number_keys_in_hash_after = len(hash_snp.keys())

    logger_instance.debug('number_keys_in_hash_before = %15s' % (number_keys_in_hash_before,))
    logger_instance.debug('number_keys_in_temphash    = %15s' % (number_keys_in_temphash,))
    logger_instance.debug('number_keys_in_hash_after  = %15s' % (number_keys_in_hash_after,))
    logger_instance.debug('difference(before-after)   = %15s' % (number_keys_in_hash_before-number_keys_in_hash_after,))
    
    return hash_snp

def check_or_insert_user(db_connection, user_id):
    logger_instance.debug("user_id       = %s" % (user_id,))
    res = db_utils.db_select_one(db_connection, select_user_query, (user_id,))
    if res == None:
        db_utils.db_insert_no_auto_id(db_connection, insert_user_query, (user_id,))
        logger_instance.debug('New user ID inserted (ID=%s)' % (user_id,))

def insert_all_genotypes(db_connection, hash_snp, hash_allele, id_file, genotype_data):
    logger_instance.debug("id_file       = %s" % (id_file,))
    to_insert = []
    for genotype_entry in genotype_data:
        name_snp = genotype_entry['snp_id']
        allele1  = genotype_entry['allele1']
        allele2  = genotype_entry.get('allele2') # default None if not found
        id_snp   = hash_snp[name_snp]
        id_allele = hash_allele[allele1][allele2]
        to_insert.append( (id_snp, id_allele, id_file) )
    db_utils.db_insert_no_auto_id_bulk(db_connection, insert_genotype_query, to_insert, batch_size=100000)

# -------------------------------------------------------------------------------------

def check_snp_file_entries(genotype_data, hash_snp, hash_allele,remove_empty_location=True):
    """
    If any snps are not already in the db, we save them into a temporary hash for later batch deposit.
    Parameters:
    genotype_data is a list of dictionaries, one per SNP
    hash_snp is a hash of name->id mappings for SNPs in the db
    hash_allele is a hash of allele1->allele2->id mappings for alleles in the db 
    Returns:
    the constructed pair of temporary hashes
    """
    logger_instance.debug("len(genotype_data)       = %s" % (len(genotype_data),))

    hash_snp_temp = {}
    hash_allele_temp = {}
    
    for genotype_entry in genotype_data:
        name_snp    = genotype_entry['snp_id']
        allele1_snp = genotype_entry['allele1']
        allele2_snp = genotype_entry.get('allele2') # default None if not found 

        # igonre entry if remove_empty_location is set to true and location is actually empty (=None,0,...)
        if remove_empty_location and not genotype_entry['location']:
            # if not present in the hash, insert it 
            if name_snp not in hash_snp:
                if name_snp not in hash_snp_temp:
                    hash_snp_temp[name_snp] = (genotype_entry['chromosome'], genotype_entry['location'])
            # check if alleles are already in the allele hash
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

    logger_instance.info("data_dir            = %s" % (data_dir,))
    logger_instance.info("data_dir_genotype   = %s" % (data_dir_genotype,))
    logger_instance.info("data_dir_phenotype  = %s" % (data_dir_phenotype,))
    logger_instance.info("data_dir_annotation = %s" % (data_dir_annotation,))
    logger_instance.info("mapping_dir         = %s" % (mapping_dir,))
    
    # load chromosome mappings
    mappings = {}
    mappings['chromosome'] = read_genotypes.load_mapping(mapping_dir,'chromosome')

    # get db connection    
    db_connection = db_connect()
    hash_allele = set_up_alleles_from_db(db_connection)
    hash_snp = set_up_snps_from_db(db_connection)
    hash_method = set_up_geno_methods_from_db(db_connection)
    
    #for i in range(2,170):
    #for user_id in [288, 305, 339, 4070, 4088, 4170, 2566, 4120, 1004, 927,937,1497]: # 885, quick alternative: 937
    for user_id in range(1,6000): # 885, quick alternative: 937
        snp_data = read_genotypes.read_snps_by_user(user_id, data_dir_genotype, mappings)
        for (filename, method, genotype_data) in snp_data:
            # ensure that users exists in the data base - moved to here, so unneccesry users are created
            check_or_insert_user(db_connection, user_id)
            logger_instance.debug('%s\t%s\t%s' % (filename, method, len(genotype_data),))
            (hash_snp_temp, hash_allele_temp) = check_snp_file_entries(genotype_data, hash_snp, hash_allele)
            hash_allele = insert_new_alleles_into_db(db_connection, hash_allele, hash_allele_temp)

            # assumption! that method is in the db and therefore in the hash. But there are very few methods so more efficient to assume than check.
            file_id = select_or_insert_genotype_file(db_connection, filename, user_id, hash_method[method])

            # add or lookup all the snps ids in snp table or hash (name, chromosome, location)
            hash_snp = insert_new_snps_into_db(db_connection, hash_snp, hash_snp_temp)

            # add all the genotypes : snp_id, allele_id, file_id
            insert_all_genotypes(db_connection, hash_snp, hash_allele, file_id, genotype_data)
            
