import pymysql
import sys
import traceback
import getopt

def usage():
    print("-h hostname -d dbname -u username")

def get_db_params():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:d:u:", ["host=", "database=", "user="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    hostname = None
    dbname   = None
    username = None
    for o, a in opts:
        if o == "-h":
            hostname = a
        elif o =="-d":
            dbname = a
        elif o == "-u":
            username = a
        else:
            usage()
            sys.exit(2)
            
    print("Password:")
    pword = sys.stdin.readline().strip()

    return {'hostname':hostname, 'dbname':dbname, 'username':username, 'pword':pword}


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


