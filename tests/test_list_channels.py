'''Test list_channels lambda function'''
# pylint: disable=protected-access
# pylint: disable=wrong-import-position
# pylint: disable=redefined-outer-name
import os, json, mock, boto3, pytest
from unittest.mock import patch, Mock, MagicMock

from tests.conftest import setup_mock_slack_helpers

# begin testing lambda function

def test_list_channels():
    paginated_api_call_mock_return_data = {
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

    started_patcher = setup_mock_slack_helpers({'paginated_api_call' : paginated_api_call_mock_return_data })

    import functions.list_channels.lambda_function as lambda_function

    result = lambda_function.handle_state()

    assert result == { "channels": paginated_api_call_mock_return_data }

    started_patcher.stop()

