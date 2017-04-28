import pymysql
import sys
import traceback
import getopt
import os.path

def usage():
    print("-h hostname -d dbname -u username")

def get_db_params_from_config(config_file='openSNPAnalysisDB.cfg'):
    ret_val = None
    if os.path.exists(config_file):
        ret_val = {}
        with open(config_file) as fh:
            data = fh.readlines()
            for line in data:
                (dbKey,dbVal) = line.strip().split(':')
                ret_val[dbKey] = dbVal
    else:
        ret_val = None
    return ret_val
    
def get_db_params():
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:d:u:c:", ["host=", "database=", "user=","config="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    hostname    = None
    dbname      = None
    username    = None
    config_file = None
    
    for o, a in opts:
        if o == "-h":
            hostname = a
        elif o =="-d":
            dbname = a
        elif o == "-u":
            username = a
        elif o == "-c":
            config_file = a
        else:
            usage()
            sys.exit(2)
    ret_val = {}
    if config_file:
        ret_val = get_db_params_from_config(config_file)
    else:
        print("Password:")
        pword = sys.stdin.readline().strip()
        ret_val = {'hostname':hostname, 'dbname':dbname, 'username':username, 'pword':pword}
    return ret_val


# ------------------------------------------------------------------------------
# Generic db queries

def db_select_one(db, query, data):
    """Select a single row only"""
    cursor = db.cursor()

    try:
        cursor.execute(query, data)
    except pymysql.MySQLError:
        sys.stderr.write("Error from MySQL:\n" + query + "\n")
        sys.stderr.write(repr(data) + "\n")
        traceback.print_exc()
        cursor.close()
        return False
    result = cursor.fetchone()
    
    cursor.close()
    return result

def db_insert_no_auto_id(db, query, data):
    """For queries where there is no insertion id created, or where we don't care about getting it back"""
    cursor = db.cursor()

    try:
        cursor.execute(query, data)
    except pymysql.MySQLError:
        sys.stderr.write("Error from MySQL:\n" + query + "\n")
        sys.stderr.write(repr(data) + "\n")
        traceback.print_exc()
        cursor.close()
        sys.exit(1)
        return False

    cursor.close()
    db.commit()
    return True




def db_insert_auto_id(db, query, data):
    """For queries where we want to know the auto increment id that was given""" 
    cursor = db.cursor()
    
    try:
        cursor.execute(query, data)
    except pymysql.MySQLError:
        sys.stderr.write("Error from MySQL:\n" + query + "\n")
        sys.stderr.write(repr(data) + "\n")
        traceback.print_exc()
        cursor.close()
        sys.exit(1)
        return -1

    db_id = db.insert_id()

    cursor.close()
    db.commit()
    return db_id

def db_insert_auto_id_bulk(db, query, data):
    """For queries where we want to know the auto increment id that was given, insertion in one single batch"""
    cursor = db.cursor()
    
    try:
        cursor.executemany(query, data)
    except pymysql.MySQLError:
        sys.stderr.write("Error from MySQL:\n" + query + "\n")
        sys.stderr.write(repr(data) + "\n")
        traceback.print_exc()
        cursor.close()
        sys.exit(1)
        return -1

    select_last_id_query = 'SELECT LAST_INSERT_ID() AS id'
    try:
        db_id_start = cursor.execute(select_last_id_query)
    except pymysql.MySQLError:
        sys.stderr.write("Error from MySQL:\n" + select_last_id_query + "\n")
        sys.stderr.write(repr(data) + "\n")
        traceback.print_exc()
        cursor.close()
        sys.exit(1)
        return -1

    
    db_id_end   = db.insert_id()

    cursor.close()
    db.commit()
    print('db_id_start',db_id_start,'db_id_end',db_id_end)
    return db_id_start,db_id_end
    



#def db_select_all(db, query, data):
def db_select_all(db, query, data=None):
    """Select a all rows"""
    cursor = db.cursor()

    try:
        cursor.execute(query, data)
    except pymysql.MySQLError:
        sys.stderr.write("Error from MySQL:\n" + query + "\n")
        sys.stderr.write(repr(data) + "\n")
        traceback.print_exc()
        cursor.close()
        return False
    result = cursor.fetchall()
    cursor.close()
    return result

