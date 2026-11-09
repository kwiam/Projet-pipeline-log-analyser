import logging
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "logs"


def get_logger(module_name):
    LOG_DIR.mkdir(exist_ok=True)
    logger = logging.getLogger(module_name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        log_format = logging.Formatter(
            "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"
        )

        module_file = logging.FileHandler(LOG_DIR / f"{module_name}.log", encoding="utf-8")
        module_file.setLevel(logging.INFO)
        module_file.setFormatter(log_format)

        errors_file = logging.FileHandler(LOG_DIR / "errors.log", encoding="utf-8")
        errors_file.setLevel(logging.ERROR)
        errors_file.setFormatter(log_format)

        logger.addHandler(module_file)
        logger.addHandler(errors_file)
    return logger