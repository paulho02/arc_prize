import logging
import inspect
import os


class ClassNameFormatter(logging.Formatter):
    def format(self, record):
        record.message = record.getMessage()
        record.asctime = self.formatTime(record, self.datefmt)
        return f"[{record.asctime}][][{record.name}][{record.levelname}]: {record.message}"


def setup_logger(name, level=logging.INFO, log_file="logs/app.log", to_console=True) -> logging.Logger:
    # Ensure directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = ClassNameFormatter()

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Optional console handler
    if to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
