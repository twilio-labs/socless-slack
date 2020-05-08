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
from socless import socless_bootstrap
from slack_helpers import slack_client, find_user, get_profile_via_id
import os


def handle_state(username="", slack_id="", exclude_bots="false"):
    """Get a slack user's profile from their username or slack_id.

    Params:
        username: User's Slack name ex. ubalogun 
        slack_id: user's Slack ID ex. W1234567
        exclude_bots: exclude bots from search results
    Returns:
        {
            "result" : (bool)
            "id" : "W1234567",
            "name" : "ssnake",
            "profile" : {
                "first_name" : "Solid",
                "last_name" : "Snake",
                "email" : "snake@outerheaven.com"
            }
        }
    """
    exclude_bots = True if exclude_bots == "true" else False
    result = {
        "result": "true",
        "id": slack_id,
        "username": username,
        "profile": {},
    }
    if slack_id:
        profile = get_profile_via_id(slack_id)
        result["username"] = profile["display_name"]
    elif username:
        search_result = find_user(username)
        user = search_result.get("user")
        if not user or exclude_bots and user["is_bot"]:
            return {"result": "false"}
        result["id"] = user["id"]
        result["name"] = user.get("name") or "N/A"
        profile = user.get("profile", {})

    # Create result Profile from subset of Slack Profile fields
    result["profile"]["first_name"] = profile.get("first_name") or "N/A"
    result["profile"]["last_name"] = profile.get("last_name") or "N/A"
    result["profile"]["email"] = profile.get("email") or "N/A"
    return result


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
