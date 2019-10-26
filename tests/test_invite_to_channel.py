'''Test invite_to_channel lambda function'''
# pylint: disable=protected-access
# pylint: disable=wrong-import-position
# pylint: disable=redefined-outer-name
import os, json, mock, boto3, pytest
from unittest.mock import patch, Mock, MagicMock

# import common_files.slack_helpers as slack_helpers
from tests.conftest import setup_mock_common_files

# begin testing lambda function
import functions.invite_to_channel.lambda_function as lambda_function

@patch('slack.WebClient.conversations_invite')
def test_invite_to_channel(slack_conversations_invite_mock):
    channel_invite_mock_return_data = {
        "ok": True,
        "channel": {
            "id": "C012AB3CD",
            "name": "general",
            "is_channel": True,
            "is_group": False,
            "is_im": False,
            "created": 1449252889,
            "creator": "W012A3BCD",
            "is_archived": False,
            "is_general": True,
            "unlinked": 0,
            "name_normalized": "general",
            "is_read_only": False,
            "is_shared": False,
            "is_ext_shared": False,
            "is_org_shared": False,
            "pending_shared": [],
            "is_pending_ext_shared": False,
            "is_member": True,
            "is_private": False,
            "is_mpim": False,
            "last_read": "1502126650.228446",
            "topic": {
                "value": "For public discussion of generalities",
                "creator": "W012A3BCD",
                "last_set": 1449709364
            },
            "purpose": {
                "value": "This part of the workspace is for fun. Make fun here.",
                "creator": "W012A3BCD",
                "last_set": 1449709364
            },
            "previous_names": [
                "specifics",
                "abstractions",
                "etc"
            ],
            "num_members": 23,
            "locale": "en-US"
        }
    }
    slack_conversations_invite_mock.return_value = channel_invite_mock_return_data

    result = lambda_function.handle_state('C012AB3CD', 'WX8675309')

    assert result == { 'created_channel_id': 'C012AB3CD', 'ok': True }

@patch('slack.WebClient.conversations_invite')
def test_invite_to_channel_failure(slack_conversations_invite_mock):
    channel_invite_mock_return_data = {
        "ok": False,
        "error": "method_not_supported_for_channel_type"
    }

    slack_conversations_invite_mock.return_value = channel_invite_mock_return_data

    result = lambda_function.handle_state('C012AB3CD', 'WX8675309')

    assert result == {
        "ok": False,
        "error": "<class 'KeyError'> 'channel' {'ok': False, 'error': 'method_not_supported_for_channel_type'}"
    }
