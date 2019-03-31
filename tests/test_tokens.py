import os
import unittest.mock

import botocore.session
import botocore.stub
import pytest

import lipwig.tokens


def test_get_token_from_environ(monkeypatch):
    """Tests getting a token from the environment."""
    service = 'test'
    key = 'TEST_TOKEN'
    token = 'test_token'
    lipwig.tokens._SERVICES[service] = {'env': key}
    key = lipwig.tokens._SERVICES[service]['env']
    monkeypatch.setenv(key, token)
    assert lipwig.tokens.get_token(service) == token


def test_get_token_from_ssm():
    service = 'test'
    env_key = 'TEST_TOKEN'
    ssm_key = '/Lipwig/TestToken'
    token = 'test_token'
    lipwig.tokens._SERVICES[service] = {'env': env_key, 'ssm': ssm_key}
    assert env_key not in os.environ
    ssm = botocore.session.get_session().create_client('ssm')
    with unittest.mock.patch('lipwig.tokens.boto3.client') as mock_client:
        mock_client.return_value = ssm
        with botocore.stub.Stubber(ssm) as stubber:
            stubber.add_response(
                'get_parameters',
                {
                   'Parameters': [{
                      'Name': ssm_key,
                      'Type': 'String',
                      'Value': token,
                      "Version": 1
                   }],
                   'ResponseMetadata': {'HTTPStatusCode': 200}
                },
                {
                    'Names': [ssm_key],
                    'WithDecryption': True
                })
            assert lipwig.tokens.get_token(service) == token


def test_get_missing_token():
    service = 'test'
    env_key = 'TEST_TOKEN'
    ssm_key = '/Lipwig/TestToken'
    lipwig.tokens._SERVICES[service] = {'env': env_key, 'ssm': ssm_key}
    assert env_key not in os.environ
    ssm = botocore.session.get_session().create_client('ssm')
    with unittest.mock.patch('lipwig.tokens.boto3.client') as mock_client:
        mock_client.return_value = ssm
        with botocore.stub.Stubber(ssm) as stubber:
            stubber.add_response(
                'get_parameters',
                {
                   'Parameters': [],
                   'InvalidParameters': [ssm_key],
                   'ResponseMetadata': {'HTTPStatusCode': 200}
                },
                {
                    'Names': [ssm_key],
                    'WithDecryption': True
                })
            with pytest.raises(lipwig.tokens.TokenNotFoundError) as err:
                lipwig.tokens.get_token(service)
            assert service == str(err.value)
