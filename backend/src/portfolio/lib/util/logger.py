import sys

from loguru import logger


def setup_logger() -> None:
	_ = logger.add(sys.stderr, level="INFO")
