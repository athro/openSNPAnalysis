import sys
import os.path
#import getopt
import pymysql
import csv
#import traceback
import db_utils

debug = True

insert_user_query        = "insert into user (id) values (%s)"
insert_pheno_name_query  = "insert into phenotype (name) values (%s)"
insert_pheno_value_query = "insert into phenotype_value (id_pheno, value) values (%s, %s)"
insert_pheno_user_query  = "insert into pheno_user (id_pheno, id_user, id_phenotype_value) values (%s, %s, %s)"
select_pheno_val_query   = "select id from phenotype_value where id_pheno = %s and value = %s"
select_user_query        = "select id from user where id = %s"

phenotypes_to_avoid = ['Darkn'] # There are two phenotypes with this same name. Neither have useful values.

# ---------------------------------------------------------------------


def insert_phenotype_names(db, names):
    """Returns a list of the autoincrement ids that were inserted, for use later"""
    ids = []
    for name in names:
        if name in phenotypes_to_avoid:
            ids.append(None)
        else:
            db_id = db_utils.db_insert_auto_id(db, insert_pheno_name_query, (name,))
            if db_id == -1:
                sys.stderr("Can't insert pheno name: <<" + name + ">>")
                sys.exit(1)
            else:
                ids.append(db_id)
    return ids


def insert_phenotype_values(db, pheno_vals, pheno_names, pheno_db_ids):
    for (name, db_id) in zip(pheno_names, pheno_db_ids):
        if name in phenotypes_to_avoid:
            continue
        for val in pheno_vals[name]:
            if val != '-': # ignore '-' values (no phenotype entry)
                db_utils.db_insert_no_auto_id(db, insert_pheno_value_query, (db_id, val))


def insert_pheno_users(db, users_vals, pheno_names, pheno_db_ids):
    # Construct the mapping from pheno names to pheno ids
    id_lookup = {}
    for (pheno_name, db_id) in zip(pheno_names, pheno_db_ids):
        id_lookup[pheno_name] = db_id

    # Now loop for each user, then each value for that user
    for user_id in users_vals:
        for (pheno_name, val) in zip(pheno_names, users_vals[user_id]):
            if val == '-' or pheno_name in phenotypes_to_avoid:
                continue # don't bother with null values
            print(select_pheno_val_query, pheno_name, id_lookup[pheno_name], val)
            [val_id] = db_utils.db_select_one(db, select_pheno_val_query, (id_lookup[pheno_name], val)) #should really check ok 
            print(user_id, val_id, pheno_name)
            db_utils.db_insert_no_auto_id(db, insert_pheno_user_query, (id_lookup[pheno_name], user_id, val_id)) 


def user_already_in_db(db, user_id):
    result = db_utils.db_select_one(db, select_user_query, (user_id,))
    if not result:
        return False
    else:
        return True

    
def add_phenotypes(db, filename):
    with open(filename) as f:
        r = csv.reader(f, delimiter=';')
        pheno_names = next(r)[1:]
        pheno_db_ids = insert_phenotype_names(db, pheno_names)
        pheno_vals = {} # will be a dict of dicts
        users_vals = {} # will be a dict of lists
        for pheno_name in pheno_names:
            pheno_vals[pheno_name] = {}

        print("Inserting users")
        for row in r:
            user_id = int(row[0])
            if user_already_in_db(db, user_id):
                # don't insert duplicate users
                continue
            db_utils.db_insert_no_auto_id(db, insert_user_query, (user_id,))
            users_vals[user_id] = row[1:]

            # gather unique values for each phenotype
            phenos = zip(pheno_names, row[1:])
            for (name, val) in phenos:
                pheno_vals[name][val] = 0
                
        insert_phenotype_values(db, pheno_vals, pheno_names, pheno_db_ids)
        insert_pheno_users(db, users_vals, pheno_names, pheno_db_ids)




if __name__ == '__main__':
    data_dir            = '..'+os.path.sep+'..'+os.path.sep+'data'
    data_dir_genotype   = '%s%sgenotypes' % (data_dir,os.path.sep)
    data_dir_phenotype  = '%s%sphenotypes' % (data_dir,os.path.sep)
    data_dir_annotation = '%s%sannotation' % (data_dir,os.path.sep)
    
    clean_pheno_file    = "%s%sphenotypes_201604281702.csv.clean.csv" % (data_dir_phenotype,os.path.sep)

    db_params = db_utils.get_db_params()
    # Open DB connection
    try:
        db = pymysql.connect( host   = db_params['hostname'],
                              db     = db_params['dbname'],
                              user   = db_params['username'],
                              passwd = db_params['pword'],
                              charset= 'utf8')
    except pymysql.MySQLError:
        sys.stderr.write("Failed to connect to database: " + db_params['dbname'] + " on " + db_params['hostname'] + "\n")
        sys.exit(1)
  
    add_phenotypes(db, clean_pheno_file)

    db.close()
