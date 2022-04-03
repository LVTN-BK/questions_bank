import inspect
import logging
import logging.config
from os import path
from os.path import dirname
import inspect
from celery.app.log import TaskFormatter

log_file_path = path.join(
    dirname(
        dirname(path.abspath(__file__))
    ), 'masterdata/logger.conf')
print(log_file_path)
logging.config.fileConfig(log_file_path)




def logger(name: str = None) -> (logging.Logger):
    if name is None:
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        name = module.__file__
    logger = logging.getLogger(name)
    logger.setLevel(level=logging.INFO)

    sh = logging.StreamHandler()
    sh.setFormatter(TaskFormatter('%(asctime)s : [%(filename)20s:%(lineno)6d] - %(levelname)s: - %(message)s'))
    logger.setLevel(logging.INFO)
    logger.addHandler(sh)

    return logger
