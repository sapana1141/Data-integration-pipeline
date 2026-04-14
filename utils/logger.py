
# import logging

# def get_logger():

#     logger = logging.getLogger("pipeline")

#     if not logger.handlers:

#         logger.setLevel(logging.INFO)

#         handler = logging.FileHandler("pipeline.log")

#         formatter = logging.Formatter(
#             "%(asctime)s | %(levelname)s | %(message)s"
#         )

#         handler.setFormatter(formatter)

#         logger.addHandler(handler)

#     return logger


import logging
from logging.handlers import RotatingFileHandler


def get_logger(name="pipeline"):
  
    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if not logger.handlers:

        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        # File handler with rotation (5MB per file, keep 3 backups)
        file_handler = RotatingFileHandler(
            f"{name}.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=3
        )
        file_handler.setFormatter(formatter)

        # Console handler (prints logs in terminal)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

