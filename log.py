from datetime import datetime
import logging


def init_log(log_file=None):
    if log_file is None:
        log_file = 'app_{}.log'.format(datetime.now().strftime('%Y%m%d'))
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(module)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)

    logging.getLogger().handlers = []
    logging.getLogger().addHandler(ch)
    logging.getLogger().addHandler(fh)
    logging.getLogger().setLevel(logging.INFO)

    logging.info('init logging file [%s]' % log_file)