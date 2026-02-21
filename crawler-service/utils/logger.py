"""
Configures and provides a standardized logger for the application.
"""
import logging

def get_logger(name: str) -> logging.Logger:
    """
    Retrieves a configured logger instance.

    This function ensures that a logger is configured with a stream handler
    and a standard formatter. It prevents duplicate handlers from being added
    if the logger is requested multiple times.

    Args:
        name (str): The name of the logger, typically `__name__`.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger