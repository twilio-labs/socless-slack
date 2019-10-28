'''Test send_dialog lambda function'''
# pylint: disable=protected-access
# pylint: disable=wrong-import-position
# pylint: disable=redefined-outer-name
import os, json, mock, boto3, pytest
from unittest.mock import patch, Mock, MagicMock

# from tests.conftest import setup_mock_socless, setup_mock_slack_helpers
from tests.conftest import setup_mock_slack_helpers

# begin testing lambda function

# def test_send_dialog():
#     paginated_api_call_mock_return_data = {
        
#     }

#     started_patcher = setup_mock_slack_helpers('paginated_api_call', paginated_api_call_mock_return_data)

#     import functions.send_dialog.lambda_function as lambda_function

#     result = lambda_function.handle_state(context, receiver, target_type, target, text)

#     assert result == { "channels": paginated_api_call_mock_return_data }

#     started_patcher.stop()

def test_send_dialog_incomplete_inputs():
    slack_helpers_patcher = setup_mock_slack_helpers()

    import functions.send_dialog.lambda_function as lambda_function

    with pytest.raises(Exception): #! DELETE : Fix the context object, this test is not correct yet
        result = lambda_function.handle_state(context={},receiver="asdf",target="asdf",target_type="asdf",message_template="")

    slack_helpers_patcher.stop()
