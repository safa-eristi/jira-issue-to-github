import logging

general_logger = logging.getLogger("general_logger")
fail_logger = logging.getLogger("fail_logger")
def log(level, message):
    general_logger.log(level, message)

def fail_log(level, message):
	fail_logger.log(level, message)
