from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def debug_print(*args, **kwargs):
    """
    Print debug messages only when DEBUG is True
    Usage:
        debug_print("This is a debug message")
        debug_print("Variable value:", some_variable)
    """
    if settings.DEBUG:
        print(*args, **kwargs)
        
def debug_log(message, level=logging.DEBUG):
    """
    Log debug messages only when DEBUG is True
    Usage:
        debug_log("This is a debug message")
        debug_log("Error occurred", level=logging.ERROR)
    """
    if settings.DEBUG:
        logger.log(level, message)