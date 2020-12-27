import os
import logging.config

DATA_DIR = 'data'
LOG_DIR = 'logs'

if os.path.exists(LOG_DIR) is False:
    os.mkdir(LOG_DIR)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)-6s [%(module)-21s:%(lineno)-3s] %(message)s'
        },
    },
    'handlers': {
        'stdout': {
            'level': 'INFO',
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'file': {
            'level': 'INFO',
            'formatter': 'default',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'app.log'),
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 10
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['stdout', 'file'],
            'level': 'INFO',
            'propagate': True
        },
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
