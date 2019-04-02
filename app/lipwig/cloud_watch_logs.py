"""Log a message to CloudWatch Logs."""
import json
import logging
import os
from typing import Any

logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', logging.INFO))


def lambda_handler(event: dict, context: Any) -> None:
    logger.info(f'New event:\n{json.dumps(event, indent=2)}')
