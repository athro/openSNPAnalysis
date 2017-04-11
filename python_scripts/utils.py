

def inc_hash(the_hash,the_key):
    try:
        the_hash[the_key]
    except:
        the_hash[the_key] = 0
        pass
    finally:
        the_hash[the_key] += 1

def inc_double_key_hash(the_hash,the_key1,the_key2):
    try:
        the_hash[the_key1]
    except:
        the_hash[the_key1] = {}
        pass
    try:
        the_hash[the_key1][the_key2]
    except:
        the_hash[the_key1][the_key2] = 0
        pass
    print(the_hash[the_key1][the_key2])
    the_hash[the_key1][the_key2] += 1
    
def insert_double_key_hash(the_hash,the_key1,the_key2,the_value):
    try:
        the_hash[the_key1]
    except:
        the_hash[the_key1] = {}
    the_hash[the_key1][the_key2] = the_value
    
        
def has_double_key_hash(the_hash,the_key1,the_key2):
    return_value = False
    try:
        the_hash[the_key1][the_key2]
        return_value = True
    except:
        pass
    return return_value

        
