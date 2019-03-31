"""Retrieve services tokens from the environment / SSM ParameterStore."""
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', logging.INFO))

_SERVICES = {
    'slack': {
        'env': 'SLACK_TOKEN',
        'ssm': '/Lipwig/SlackToken'
    }
}
"""Service to key names mapping.

For every service supported by Lipwig that requires an API token for access, this dict maps the service name to
keys used to search for its token in the environment and in SSM ParameterStore.
"""


def get_token(service: str) -> str:
    """Retrieves the token for the specified service.

    Searches for the token in the environment, then in SSM ParameterStore.

    Args:
        service: The name of the service.
            The name must be present in the SERVICES dict.

    Returns:
        The token for the service.

    Raises:
        TokenNotFoundError: If the token is found in neither the environment nor SSM ParameterStore.
    """
    logger.debug(f'Looking for the {service} token in an environment variable')
    key = _SERVICES[service]['env']
    if key in os.environ:
        return os.environ[key]
    logger.debug(f'Looking for the {service} token in SSM ParameterStore')
    ssm = boto3.client('ssm')
    key = _SERVICES[service]['ssm']
    response = ssm.get_parameters(Names=[key], WithDecryption=True)
    if response['Parameters']:
        return response['Parameters'][0]['Value']
    logger.error(f'{service} token not found in neither environment variables nor SSM ParameterStore!')
    raise(TokenNotFoundError(service))


class TokenNotFoundError(Exception):
    """Exception raised when the application cannot find the token for some service.

    Attributes:
        service: The name of the service whose token was not found.
    """

    def __init__(self, service: str):
        self.service = service
