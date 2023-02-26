import logging

logger = logging.getLogger('PDF Tool')
logger.setLevel(logging.DEBUG)

# create a file handler
file_handler = logging.FileHandler('pdf_tool_log_file.log')
file_handler.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# create a stream handler to log to console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def set_log_level_for_console(level: int):
    stream_handler.setLevel(level)
