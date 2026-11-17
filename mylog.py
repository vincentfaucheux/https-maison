import logging
import time

ref_time = None
szPath = None
logger = None
handler = None

def start_log( inszPath) :
    global ref_time
    global szPath
    ref_time = time.localtime()
    szPath = inszPath
    global logger
    global handler
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    #logger.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    year = str( ref_time.tm_year)
    month = str( f"{ref_time.tm_mon:02d}")
    handler = logging.FileHandler(szPath + f"/{year}_{month}_server.log")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

def close_log() :
    global handler
    handler.close()

def check_change_file() :
    global ref_time
    global szPath
    global logger
    global handler
    curr_time = time.localtime()
    if(( curr_time.tm_year != ref_time.tm_year) or (curr_time.tm_mon != ref_time.tm_mon)) :
        logger.removeHandler(handler)
        handler.close()
        ref_time = curr_time
        year = str( ref_time.tm_year)
        month = str( f"{ref_time.tm_mon:02d}")
        handler = logging.FileHandler(szPath + f"/{year}_{month}_server.log")
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)

def info_log( szInfo) :
    global logger
    #check if the log file should be changed
    check_change_file()
    #log the info
    logger.info( szInfo)

def error_log( szError) :
    global logger
    #check if the log file should be changed
    check_change_file()
    #log the error
    logger.error( szError)

def warning_log( szWarning) :
    global logger
    #check if the log file should be changed
    check_change_file()
    #log the warning
    logger.warning( szWarning)