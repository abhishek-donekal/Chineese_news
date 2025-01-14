import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s       - %(message)s [%(filename)s:%(lineno)d]',  # Custom log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Custom date format
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)