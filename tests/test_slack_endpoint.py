'''Test slack_endpoint lambda function'''
# pylint: disable=protected-access
# pylint: disable=wrong-import-position
# pylint: disable=redefined-outer-name
import os, json, mock, boto3, pytest
from unittest.mock import patch, Mock, MagicMock

# begin testing lambda function

@patch('slack.WebClient.conversations_setTopic')
def test_slack_endpoint_incomplete_inputs(slack_conversations_set_topic_mock):
    conversations_set_topic_mock_return_data = {
        #! DELETE Fill this in with slack response when you get internet again
    }

    import functions.slack_endpoint.lambda_function as lambda_function

    result = lambda_function.handle_state(channel_id="WX01234567", topic="test topic")
    
