'''Test create_channel'''
# pylint: disable=protected-access
# pylint: disable=wrong-import-position
# pylint: disable=redefined-outer-name
import os, json, mock, boto3, pytest
from unittest.mock import patch, Mock

# begin testing lambda function
import functions.create_channel.lambda_function as lambda_function

@patch('functions.create_channel.lambda_function.slack')
def test_create_channel(slack_client_conversations_create_mock):
    #setup mock slack api
    slack_client_conversations_create_mock.WebClient().conversations_create.return_value = {
        "channel" : {
            "id" : 'Wx8675309'
        }
    }

    result = lambda_function.handle_state('testing', False)
    assert result["ok"] == True
    assert result["created_channel_id"] == 'Wx8675309'
    assert result["channel_name"] == 'testing'

@patch('functions.create_channel.lambda_function.slack')
def test_create_channel(slack_client_conversations_create_mock):
    #setup mock slack api
    slack_client_conversations_create_mock.WebClient().conversations_create.return_value = {
        "ok": False,
        "error": "name_taken",
        "detail": "A channel cannot be created with the given name."
    }

    result = lambda_function.handle_state('testing', False)
    assert result["ok"] == False
    assert result["error"] == "<class 'KeyError'> 'channel' {'ok': False, 'error': 'name_taken', 'detail': 'A channel cannot be created with the given name.'}"
