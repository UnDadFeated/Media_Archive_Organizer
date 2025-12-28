import logging
import os
import sys

def setup_logger():
    # Determine log path
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        # Running from src/ui/app.py -> src/ui -> src -> root
        # Or launched from launcher.py (root)
        base_dir = os.getcwd()
        
    log_file = os.path.join(base_dir, 'media_organizer_debug.log')
    
    # Reset handlers if re-initialized
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        
    logging.basicConfig(
        filename=log_file,
        filemode='w', # Overwrite each run
        format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        level=logging.DEBUG
    )
    
    # Also log to console for dev
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    logging.getLogger('').addHandler(console)
    
    logging.info(f"=== Application Started (v2.0 Check) ===")
    logging.info(f"Log File: {log_file}")
    logging.info(f"CWD: {os.getcwd()}")
    
    return logging.getLogger('MediaOrganizer')
