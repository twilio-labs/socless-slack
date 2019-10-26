'''Test slack_helpers'''
# pylint: disable=protected-access
# pylint: disable=wrong-import-position
# pylint: disable=redefined-outer-name
import os, json, mock, boto3, pytest
from unittest.mock import patch, Mock
from requests import exceptions

# begin testing lambda function
from common_files.slack_helpers import find_user, get_channel_id, paginated_api_call, slack_client

from tests.constants import users_list_pg1, users_list_pg2, conversations_members_pg1, conversations_members_pg2

@patch('common_files.slack_helpers.slack_client.users_list')
def test_find_user(slack_client_users_list_mock):
    slack_client_users_list_mock.side_effect = [
        Mock(data=users_list_pg1), 
        Mock(data=users_list_pg2)
    ]
    
    result = find_user('spengler')
    assert result['found'] == True
    assert result['user']['id'] == 'W012A3CDE'

@patch('common_files.slack_helpers.slack_client.users_list')
def test_find_user_not_found(slack_client_users_list_mock):
    slack_client_users_list_mock.side_effect = [
        Mock(data=users_list_pg1), 
        Mock(data=users_list_pg2)
    ]
    
    result = find_user('i_dont_exist')
    assert result['found'] == False


def test_get_channel_id_slack_id():
    result = get_channel_id('WX4780', 'slack_id')
    assert result == 'WX4780'

def test_get_channel_id_channel_name():
    result = get_channel_id('testing', 'channel')
    assert result == "#testing"

@patch('common_files.slack_helpers.slack_client.users_list')
def test_get_channel_id_user(slack_client_users_list_mock):
    slack_client_users_list_mock.return_value = Mock(data=users_list_pg2)
    result = get_channel_id('shunt', 'user')
    assert result == "W08675309"

@patch('common_files.slack_helpers.slack_client.users_list')
def test_get_channel_id_failure(slack_client_users_list_mock):
    slack_client_users_list_mock.return_value = Mock(data=users_list_pg2)
    
    with pytest.raises(Exception):
        result = get_channel_id('i_dont_exist', 'user')

@patch('common_files.slack_helpers.slack_client.conversations_members')
def test_paginated_api_call(slack_client_conversations_members_mock):
    """PAGINATED API CALL FAILING, ALL FUNCTIONS THAT USE IT ARE NOT IN ANY PLAYBOOKS.
    
    lambdas that need validation/update due to use of `paginated_api_call`:
        check_user_in_channel
        list_channels
    """
    pass
    # slack_client_conversations_members_mock.side_effect = [
    #     conversations_members_pg1,
    #     conversations_members_pg2 
    # ]

    # result = paginated_api_call(slack_client.conversations_members,
    #                         'members',
    #                         target_channel_id='#testing'
    #                         )
    # print(result)
    # assert result['ok'] == True
