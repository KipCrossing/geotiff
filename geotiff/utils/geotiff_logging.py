import logging
from colorlog import ColoredFormatter # type: ignore

LOG_LEVEL = logging.DEBUG
LOGFORMAT =   "(%(module)s) %(log_color)s%(levelname)s%(reset)s | %(log_color)s%(message)s%(reset)s"
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOGFORMAT)
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger('pythonConfig')
log.setLevel(LOG_LEVEL)
log.addHandler(stream)