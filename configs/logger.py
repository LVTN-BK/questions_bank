import inspect
import logging
import logging.config
import inspect


# logging.basicConfig(format='%(asctime)s : [%(filename)20s:%(lineno)6d] - %(levelname)s: - %(message)s')

def logger(name: str = None) -> (logging.Logger):
    if name is None:
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        name = module.__file__
    logger = logging.getLogger(name)
    logger.setLevel(level=logging.INFO)
    logger.basicConfig(format='%(asctime)s : [%(filename)20s:%(lineno)6d] - %(levelname)s: - %(message)s')

    return logger
