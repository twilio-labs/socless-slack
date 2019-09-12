# Copyright 2018 Twilio, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License
from socless import *
from slack_helpers import slack_client, find_user
import os


def handle_state(username,exclude_bots="false"):
    """
    Find a Slack user by their username
    Params:
        username: User's Slack name
        exclude_bots: exclude bots from search results
    """
    exclude_bots = True if exclude_bots == "true" else False
    search_result = find_user(username)
    if not search_result['found']:
        return {"result": 'false'}

    user = search_result['user']
    if exclude_bots and user['is_bot']:
        return {"result": 'false'}

    result = {}
    result['result'] = 'true'
    result['profile'] = {}
    profile = user.get('profile',{})
    result['profile']['first_name'] = profile.get('first_name') or 'N/A'
    result['profile']['last_name'] = profile.get('last_name') or 'N/A'
    result['name'] = user.get('name') or 'N/A'
    result['profile']['email'] = profile.get('email') or 'N/A'
    result["id"] = user['id']
    return result

def lambda_handler(event,context):
    return socless_bootstrap(event,context,handle_state)
