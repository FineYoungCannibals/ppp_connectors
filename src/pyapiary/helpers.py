from datetime import datetime
from dotenv import dotenv_values, find_dotenv
import logging
import os
import sys
from typing import Dict, Set, List, Any, Optional


def check_required_env_vars(config: Dict[str, str], required_vars: List[str]) -> None:
    """Ensure that the env variables required for a function are present either in \
        the .env file, or in the system's environment variables.

    Args:
        config (Dict[str, str]): the env_config variable that contains values from the .env file
        required_vars (List[str]): the env variables required for a function to successfully function
    """

    dotenv_missing_vars: Set[str] = set(required_vars) - set(config.keys())
    osenv_missing_vars: Set[str] = set(required_vars) - set(os.environ)
    missing_vars = dotenv_missing_vars | osenv_missing_vars

    if dotenv_missing_vars and osenv_missing_vars:
        print(f'[!] Error: missing required environment variables: {", ".join(missing_vars)}. '
              'Please ensure these are present either in your .env file, or in the '
              'system\'s environment variables.', file=sys.stderr)
        sys.exit(1)


def combine_env_configs() -> Dict[str, Any]:
    """Find a .env file if it exists, and combine it with system environment
        variables to form a "combined_config" dictionary of environment variables

    Returns:
        Dict: a dictionary containing the output of a .env file (if found), and
        system environment variables
    """

    env_config: Dict[str, Any] = dict(dotenv_values(find_dotenv()))

    combined_config: Dict[str, Any] = {**env_config, **dict(os.environ)}

    return combined_config


def validate_date_string(date_str: str) -> bool:
    """Validates that a date string is, well, a valid date string

    Args:
        date_str (str): a string in "YYYY-MM-DD" format

    Returns:
        bool: True or False as valid or not
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def setup_logger(
    name: str = __name__,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    use_stdout: bool = True
) -> logging.Logger:
    """
    Configures and returns a logger with optional StreamHandler and/or FileHandler.

    This function checks if a logger with the specified name already has any StreamHandler
    or FileHandler attached, and if not, it adds them according to the parameters.

    Args:
        name (str): The name of the logger to configure.
        level (int): The logging level to set for the logger. Defaults to logging.INFO.
        log_file (Optional[str]): If provided, logs will be written to this file.
        use_stdout (bool): Whether to log to standard output. Defaults to True.

    Returns:
        logging.Logger: A configured logger instance.
    """
    logger: logging.Logger = logging.getLogger(name)

    logger.setLevel(level)

    formatter = logging.Formatter(
        '[%(asctime)s]\t%(levelname)s\t%(name)s:%(lineno)d\t%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    if use_stdout and not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    if log_file and not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger
