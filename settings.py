LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'fmt': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'formatter': 'fmt',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        },
        'pixel_art': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        },
        '__main__': {  # if __name__ == '__main__'
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}
