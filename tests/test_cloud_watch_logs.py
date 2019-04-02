import json
import logging
import pathlib

from lipwig import cloud_watch_logs


def test_lambda_handler(caplog):
    path = pathlib.Path(__file__).parent / 'events' / 'text_message.json'
    event_text = path.read_text()
    event = json.loads(event_text)
    with caplog.at_level(logging.INFO):
        cloud_watch_logs.lambda_handler(event, '')
        assert event_text in caplog.text
