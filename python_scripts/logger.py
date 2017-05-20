import logging
logger_instance_initialized = False


def setup_logger(logger_name='openSNPAnalysis',log_filename='openSNPAnalysis.log',log_level=logging.DEBUG,log_format=None):
    global logger_instance_initialized
    if not logger_instance_initialized:
        # create logger 
        logger_instance = logging.getLogger(logger_name)
        logger_instance.setLevel(log_level)
        # create file handler which logs debug messages
        fh_debug = logging.FileHandler(log_filename)
        fh_debug.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch_error = logging.StreamHandler()
        ch_error.setLevel(logging.ERROR)
        # create formatter and add it to the handlers
        if log_format==None:
            log_format = '[%(asctime)s:%(filename)30s:%(lineno)5s-%(funcName)30s()] %(message)s'
            #log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
        formatter = logging.Formatter(log_format)
        fh_debug.setFormatter(formatter)
        ch_error.setFormatter(formatter)
        # add the handlers to the logger_instance
        logger_instance.addHandler(fh_debug)
        logger_instance.addHandler(ch_error)
        logger_instance.info('Logger set up')
        logger_instance_initialized = True
        return logger_instance
    else:
        logger_instance = logging.getLogger(logger_name)
        return logger_instance

