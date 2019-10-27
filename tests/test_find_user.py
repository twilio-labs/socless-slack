'''Test find_user lambda function'''
# pylint: disable=protected-access
# pylint: disable=wrong-import-position
# pylint: disable=redefined-outer-name
import os, json, mock, boto3, pytest
from unittest.mock import patch, Mock, MagicMock

from tests.conftest import setup_mock_slack_helpers

# begin testing lambda function

def test_find_user_lambda():
    find_user_mock_return_value_data = {
        "found" :  True,
        "user" : {
            "id": "W012A3CDE",
            "team_id": "T012AB3C4",
            "name": "spengler",
            "deleted": False,
            "color": "9f69e7",
            "real_name": "spengler",
            "tz": "America/Los_Angeles",
            "tz_label": "Pacific Daylight Time",
            "tz_offset": -25200,
            "profile": {
                "avatar_hash": "ge3b51ca72de",
                "status_text": "Print is dead",
                "status_emoji": ":books:",
                "real_name": "Egon Spengler",
                "display_name": "spengler",
                "real_name_normalized": "Egon Spengler",
                "display_name_normalized": "spengler",
                "email": "spengler@ghostbusters.example.com",
                "image_24": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "image_32": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "image_48": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "image_72": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "image_192": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "image_512": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "team": "T012AB3C4"
            },
            "is_admin": True,
            "is_owner": False,
            "is_primary_owner": False,
            "is_restricted": False,
            "is_ultra_restricted": False,
            "is_bot": False,
            "updated": 1502138686,
            "is_app_user": False,
            "has_2fa": False
        }
    }
    
    #setup mock find_user slack call
    started_patcher = setup_mock_slack_helpers({'find_user' : find_user_mock_return_value_data})
    
    import functions.find_user.lambda_function as lambda_function

    result = lambda_function.handle_state('spengler')

    assert result == {
        'result' : 'true',
        "id" : "W012A3CDE",
        "name" : "spengler",
        'profile' : {
            "first_name" : "N/A",
            "last_name" : "N/A",
            "email" : "spengler@ghostbusters.example.com",
        }
    }

    started_patcher.stop()

def test_find_user_lambda_not_found():
    find_user_mock_return_value_data = {
        "found" :  False,
    }
    
    #setup mock find_user slack call
    started_patcher = setup_mock_slack_helpers({'find_user' : find_user_mock_return_value_data})
    
    import functions.find_user.lambda_function as lambda_function

    result = lambda_function.handle_state('spengler')
    
    assert result == {
        'result' : 'false'
    }

    started_patcher.stop()

def test_find_user_lambda_exclude_bots():
    find_user_mock_return_value_data = {
        "found" :  True,
        "user" : {
            "id": "W012A3CDE",
            "team_id": "T012AB3C4",
            "name": "spengler",
            "deleted": False,
            "color": "9f69e7",
            "real_name": "spengler",
            "tz": "America/Los_Angeles",
            "tz_label": "Pacific Daylight Time",
            "tz_offset": -25200,
            "profile": {
                "avatar_hash": "ge3b51ca72de",
                "status_text": "Print is dead",
                "status_emoji": ":books:",
                "real_name": "Egon Spengler",
                "display_name": "spengler",
                "real_name_normalized": "Egon Spengler",
                "display_name_normalized": "spengler",
                "email": "spengler@ghostbusters.example.com",
                "image_24": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "image_32": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "image_48": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "image_72": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "image_192": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "image_512": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "team": "T012AB3C4"
            },
            "is_admin": True,
            "is_owner": False,
            "is_primary_owner": False,
            "is_restricted": False,
            "is_ultra_restricted": False,
            "is_bot": True,
            "updated": 1502138686,
            "is_app_user": False,
            "has_2fa": False
        }
    }
    
    #setup mock find_user slack call
    started_patcher = setup_mock_slack_helpers({'find_user' : find_user_mock_return_value_data})
    
    import functions.find_user.lambda_function as lambda_function

    result = lambda_function.handle_state('spengler', exclude_bots="true")
    
    assert result == {
        'result' : 'false'
    }

    started_patcher.stop()
