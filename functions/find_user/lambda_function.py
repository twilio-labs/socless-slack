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
from slack_helpers import find_user, get_user_info_via_id, get_slack_id_from_username
import os


def handle_state(username="", slack_id="", exclude_bots=False):
    """Get a slack user's profile from their username or slack_id.
    Args:
        username: User's Slack name ex. ubalogun
        slack_id: user's Slack ID ex. W1234567
        exclude_bots: exclude bots from search results
    Returns:
        {
            "result" : (bool)
            "id" : "W1234567", # Slack ID of the user
            "name" : "ssnake", # username
            "profile" : {
                "first_name" : "Solid",
                "last_name" : "Snake",
                "email" : "snake@outerheaven.com"
            }
        }
    """
    if exclude_bots and isinstance(exclude_bots, str):
        lowered = exclude_bots.lower()
        if lowered not in ["true", "false"]:
            raise Exception(
                f"Invalid value passed for arg 'exclude_bots': {exclude_bots}. Arg must be type bool or string 'true|false' "
            )
        exclude_bots = True if lowered == "true" else False

    if username and not slack_id:
        slack_id = get_slack_id_from_username(username)

    user = get_user_info_via_id(slack_id)
    profile = user.get("profile", {})

    if exclude_bots and user["is_bot"]:
        return {"result": "false"}

    result = {
        "result": "true",
        "id": user["id"],
        "name": user.get("name") or "N/A",
        "username": username if username else profile["display_name"],
        "profile": {
            "first_name": profile.get("first_name") or "N/A",
            "last_name": profile.get("last_name") or "N/A",
            "email": profile.get("email") or "N/A",
        },
    }

    return result


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
