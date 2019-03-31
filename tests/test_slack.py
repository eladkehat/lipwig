import json
import pathlib
import unittest.mock

import pytest

from lipwig import tokens


@pytest.fixture(autouse=True)
def slack_token(monkeypatch):
    monkeypatch.setenv(tokens._SERVICES['slack']['env'], 'xoxp-1234123412341234-12341234-1234')


@pytest.fixture
def expected_header():
    return 'New message on topic "ExampleTopic" received at 2019-03-31T15:12:23.345Z\nSubject: *example subject*'


@pytest.fixture
def expected_message():
    return '''*Message:*
```
{
  "Key1": "Value1",
  "Key2": {
    "Subkey21": "Value21",
    "Subkey22": 22
  }
}
```'''


@pytest.fixture
def expected_attributes():
    return '''*Attributes:*
```
{
  "Test": {
    "Type": "String",
    "Value": "TestString"
  }
}
```'''


def load_sns_event(basename):
    path = pathlib.Path(__file__).parent / 'events' / f'{basename}.json'
    return json.loads(path.read_text())['Records'][0]['Sns']


def test_text_message_event_to_slack_message_blocks(expected_header, expected_attributes):
    # Imported within the function so that the `slack_token` fixture runs first
    from lipwig import slack
    sns_event = load_sns_event('text_message')
    sections = slack.event_to_slack_message_blocks(sns_event)
    assert len(sections) == 5
    assert all([section['type'] == 'section' and section['text']['type'] == 'mrkdwn'
                for i, section in enumerate(sections) if i % 2 == 0])
    assert all([section == {'type': 'divider'} for i, section in enumerate(sections) if i % 2])
    assert sections[0]['text']['text'] == expected_header
    assert sections[2]['text']['text'] == '*Message:*\nexample message'
    assert sections[4]['text']['text'] == expected_attributes


def test_json_message_without_attributes_event_to_slack_message_blocks(expected_header, expected_message):
    from lipwig import slack
    sns_event = load_sns_event('json_message_without_attributes')
    sections = slack.event_to_slack_message_blocks(sns_event)
    assert len(sections) == 3
    assert all([section['type'] == 'section' and section['text']['type'] == 'mrkdwn'
                for i, section in enumerate(sections) if i % 2 == 0])
    assert all([section == {'type': 'divider'} for i, section in enumerate(sections) if i % 2])
    assert sections[0]['text']['text'] == expected_header
    assert sections[2]['text']['text'] == expected_message


def test_json_message_without_subjet_event_to_slack_message_blocks(expected_attributes, expected_message):
    from lipwig import slack
    sns_event = load_sns_event('json_message_without_subject')
    sections = slack.event_to_slack_message_blocks(sns_event)
    assert len(sections) == 5
    assert all([section['type'] == 'section' and section['text']['type'] == 'mrkdwn'
                for i, section in enumerate(sections) if i % 2 == 0])
    assert all([section == {'type': 'divider'} for i, section in enumerate(sections) if i % 2])
    assert sections[0]['text']['text'] == 'New message on topic "ExampleTopic" received at 2019-03-31T15:12:23.345Z'
    assert sections[2]['text']['text'] == expected_message
    assert sections[4]['text']['text'] == expected_attributes


def test_long_text_message_event_to_slack_message_blocks():
    from lipwig import slack
    long_message = 'Hello, World!\n' * 1000
    assert len(long_message) > 3000
    sns_event = load_sns_event('text_message')
    sns_event['Message'] = long_message
    sections = slack.event_to_slack_message_blocks(sns_event)
    assert len(sections[2]['text']['text']) < 3000
    assert sections[2]['text']['text'].startswith('*Message:*')


def test_long_json_message_event_to_slack_message_blocks():
    from lipwig import slack
    long_json = json.dumps(['Hello, World!'] * 1000)
    assert len(long_json) > 3000
    sns_event = load_sns_event('json_message_without_attributes')
    sns_event['Message'] = long_json
    sections = slack.event_to_slack_message_blocks(sns_event)
    assert len(sections[2]['text']['text']) < 3000
    assert sections[2]['text']['text'].startswith('Message too long. Showing raw prefix:')


def test_post_message_successfully():
    from lipwig import slack
    sns_event = load_sns_event('text_message')
    message_blocks = slack.event_to_slack_message_blocks(sns_event)
    response = {'ok': True, 'channel': 'lipwig', 'ts': '1970-01-01T00:00:00.000Z'}
    with unittest.mock.patch('lipwig.slack.slack') as mock_slack:
        mock_slack.api_call.return_value = response
        assert slack.post_message(message_blocks)
        mock_slack.api_call.assert_called_once_with(
            'chat.postMessage',
            channel='lipwig',
            blocks=message_blocks)


def test_post_message_unsuccessfully_with_custom_channel(monkeypatch):
    monkeypatch.setenv('SLACK_CHANNEL', 'test-channel')
    from lipwig import slack
    sns_event = load_sns_event('text_message')
    message_blocks = slack.event_to_slack_message_blocks(sns_event)
    response = {'ok': False, 'error': 'some_error'}
    with unittest.mock.patch('lipwig.slack.slack') as mock_slack:
        mock_slack.api_call.return_value = response
        assert not slack.post_message(message_blocks)
        mock_slack.api_call.assert_called_once_with(
            'chat.postMessage',
            channel='test-channel',
            blocks=message_blocks)


def test_lambda_handler():
    path = pathlib.Path(__file__).parent / 'events' / 'text_message.json'
    event = json.loads(path.read_text())
    sns_event = event['Records'][0]['Sns']
    from lipwig import slack
    blocks = slack.event_to_slack_message_blocks(sns_event)
    with unittest.mock.patch('lipwig.slack.post_message') as mock_post:
        slack.lambda_handler(event, '')
        assert mock_post.called_with(blocks)
