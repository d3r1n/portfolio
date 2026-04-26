import sys

from loguru import logger


def setup_logger() -> None:
	logger.add(sys.stderr, level="INFO")
