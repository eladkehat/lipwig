"""Post a message to Slack.

Requires a Slack API token to be present in either:
- An environment variable with the key "SLACK_TOKEN"
- A SSM ParameterStore parameter with the key name "/Lipwig/SlackToken"
See `lipwig.tokens` for more information.
"""
import json
import logging
import os
from typing import Any, List

import slackclient

from lipwig import tokens

logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', logging.INFO))

slack = slackclient.SlackClient(tokens.get_token('slack'))


def lambda_handler(event: dict, context: Any) -> None:
    logger.debug('Slack handler triggered')
    sns_event = event['Records'][0]['Sns']
    post_message(event_to_slack_message_blocks(sns_event))


def event_to_slack_message_blocks(sns_event: dict) -> List[dict]:
    """Constructs a Slack message from the SNS event.

    The message is layed out in Slack blocks format, using markdown.
    See: https://slack.dev/python-slackclient/basic_usage.html#customizing-a-message-s-layout

    The message attributes (if any), and the message itself, if it's in JSON format,
    are layed out as indented JSON.

    Args:
        sns_event: The "Sns" part of the event received by the handler.

    Returns:
        A list of message block sections.
    """
    def add_section(text):
        sections.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': text}})

    sections = []
    # Header
    topic = sns_event['TopicArn'].split(':')[-1]  # The topic name
    text = f'New message on topic "{topic}" received at {sns_event["Timestamp"]}'
    if sns_event['Subject']:
        text += f'\nSubject: **{sns_event["Subject"]}**'
    add_section(text)
    # Attributes (if any)
    if 'MessageAttributes' in sns_event:
        add_section(f'```json\n{json.dumps(sns_event["MessageAttributes"], indent=2)}\n```')
    # The message itself
    try:
        message = json.loads(sns_event['Message'])
        add_section(f'```json\n{json.dumps(message, indent=2)}\n```')
    except ValueError:  # The message is not JSON - probably a string.
        add_section(sns_event['Message'])
    return sections


def post_message(message_blocks: List[dict]) -> bool:
    """Posts a message to Slack.

    Args:
        message_blocks: A list of message blocks, as constructed by `event_to_slack_message_blocks()`.

    Returns:
        Whether the message was posted successfully.
    """
    channel = os.environ.get('SLACK_CHANNEL', 'lipwig')
    response = slack.api_call(
      'chat.postMessage',
      channel=channel,
      blocks=message_blocks
    )
    # If the message succeeds, `response['ok']` is `True`
    if response['ok']:
        logger.debug(f'Slack message posted to {response["channel"]}, timestamp: {response["ts"]}')
        return True
    else:
        logger.error(f'Slack message failed with error: "{response["error"]}"')
        return False
