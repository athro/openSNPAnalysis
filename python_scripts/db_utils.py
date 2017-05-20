import pymysql
import sys
import traceback
import getopt
import os.path

import logging
logger_instance = logging.getLogger('openSNPAnalysis')

def usage():
    print("-h hostname -d dbname -u username | -c configfile")

def get_db_params_from_config(config_file='openSNPAnalysisDB.cfg'):
    logger_instance.debug("config_file = <<%s>>" % (config_file,))
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
    logger_instance.debug("config = <<hostname:%s,dbname:%s,username:%s>>" % (ret_val['hostname'],ret_val['dbname'],ret_val['username'],))
    return ret_val


# ------------------------------------------------------------------------------
# Generic db queries

def db_select_one(db, query, data):
    """Select a single row only"""
    logger_instance.debug("query = <<%s>>" % (query[:100],))
    cursor = db.cursor()
    try:
        cursor.execute(query, data)
    except pymysql.MySQLError:
        err_string = "Error from MySQL:\n" + query + "\n"
        sys.stderr.write(err_string + "\n")
        logger_instance.debug(err_string)

        sys.stderr.write(repr(data) + "\n")
        logger_instance.debug(repr(data))

        traceback.print_exc()
        logger_instance.debug(traceback.format_exception())

        cursor.close()
        sys.exit(1)
        #return False
    else:
        result = cursor.fetchone()
        cursor.close()
        return result

def db_insert_no_auto_id(db, query, data):
    """For queries where there is no insertion id created, or where we don't care about getting it back"""
    logger_instance.debug("query = <<%s>>" % (query[:100],))
    cursor = db.cursor()

    try:
        cursor.execute(query, data)
    except pymysql.MySQLError:
        err_string = "Error from MySQL:\n" + query 
        sys.stderr.write(err_string + "\n")
        logger_instance.debug(err_string)

        sys.stderr.write(repr(data) + "\n")
        logger_instance.debug(repr(data))

        traceback.print_exc()
        logger_instance.debug(traceback.format_exception())

        cursor.close()
        sys.exit(1)
        #return False
    else:
        cursor.close()
        db.commit()
        return True




def db_insert_auto_id(db, query, data):
    """For queries where we want to know the auto increment id that was given""" 
    logger_instance.debug("query = <<%s>>" % (query[:100],))
    cursor = db.cursor()
    
    try:
        cursor.execute(query, data)
    except pymysql.MySQLError:
        err_string = "Error from MySQL:\n" + query 
        sys.stderr.write(err_string + "\n")
        logger_instance.debug(err_string)

        sys.stderr.write(repr(data) + "\n")
        logger_instance.debug(repr(data))

        traceback.print_exc()
        logger_instance.debug(traceback.format_exception())

        cursor.close()
        sys.exit(1)
        #return -1
    else:
        db_id = db.insert_id() 
        cursor.close()
        db.commit()
        return db_id

def db_insert_auto_id_bulk(db, query, data):
    """For queries where we want to know the auto increment id that was given, insertion in one single batch"""
    logger_instance.debug("query = <<%s>>"% (query[:100],))

    cursor = db.cursor()
    
    try:
        cursor.executemany(query, data)
    except pymysql.MySQLError:
        err_string = "Error from MySQL:\n" + query 
        sys.stderr.write(err_string + "\n")
        logger_instance.debug(err_string)

        sys.stderr.write(repr(data) + "\n")
        logger_instance.debug(repr(data))

        traceback.print_exc()
        logger_instance.debug(traceback.format_exception())

        cursor.close()
        sys.exit(1)
        #return -1
    else:
        select_last_id_query = 'SELECT LAST_INSERT_ID() AS id'
        try:
            db_id_start = cursor.execute(select_last_id_query)
        except pymysql.MySQLError:
            err_string = "Error from MySQL:\n" + select_last_id_query 
            sys.stderr.write(err_string + "\n")
            logger_instance.debug(err_string)

            sys.stderr.write(repr(data) + "\n")
            logger_instance.debug(repr(data))

            traceback.print_exc()
            logger_instance.debug(traceback.format_exception())

            cursor.close()
            sys.exit(1)
            #return -1
        else:
            db_id_end   = db_id_start + len(data) - 1 #db.insert_id()
            cursor.close()
            db.commit()
            print('db_id_start',db_id_start,'db_id_end',db_id_end)
            return db_id_start,db_id_end
    

def db_insert_no_auto_id_bulk(db, query, data, batch_size=100):
    """For queries where we don't have auto_id or don't care, insertion in one single batch"""
    logger_instance.debug("query = <<%s>>"% (query[:100],))

    data_size = len(data)
    for i in range(0, data_size-1, batch_size):
        data_batch = data[i : i+batch_size]
        cursor = db.cursor()
        try:
            cursor.executemany(query, data_batch)
        except pymysql.MySQLError:
            err_string = "Error from MySQL:\n" + query 
            sys.stderr.write(err_string + "\n")
            logger_instance.debug(err_string)

            sys.stderr.write(repr(data) + "\n")
            logger_instance.debug(repr(data))

            traceback.print_exc()
            logger_instance.debug(traceback.format_exception())

            cursor.close()
            sys.exit(1)
        else:
            cursor.close()
            db.commit()
    return True
    



#def db_select_all(db, query, data):
def db_select_all(db, query, data=None):
    """Select all rows"""
    logger_instance.debug("query = <<%s>>"% (query[:100],))
    cursor = db.cursor()

    try:
        cursor.execute(query, data)
    except pymysql.MySQLError:
        err_string = "Error from MySQL:\n" + query 
        sys.stderr.write(err_string + "\n")
        logger_instance.debug(err_string)

        sys.stderr.write(repr(data) + "\n")
        logger_instance.debug(repr(data))

        traceback.print_exc()
        logger_instance.debug(traceback.format_exception())

        cursor.close()
        sys.exit(1)
        #return False
    else:
        result = cursor.fetchall()
        cursor.close()
        return result

