import logging
import os
import sys

def setup_logger():
    # Reset handlers if re-initialized
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        
    # User requested NO LOG FILE. 
    # We only log to console (which is hidden in GUI mode unless debugged)
    
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        level=logging.DEBUG
    )
    
    # Explicit connection to stdout just in case basicConfig didn't pick it up (it usually does if no filename)
    # console = logging.StreamHandler()
    # console.setLevel(logging.DEBUG)
    # logging.getLogger('').addHandler(console)
    
    logging.info(f"=== Application Started (v2.1 NoLog) ===")
    
    return logging.getLogger('MediaOrganizer')
