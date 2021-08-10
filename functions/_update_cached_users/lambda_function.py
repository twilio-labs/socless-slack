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
from slack_helpers import SlackHelper, CACHE_USERS_TABLE
import boto3

if not CACHE_USERS_TABLE:
    raise Exception(
        "env var CACHE_USERS_TABLE is not set, please check socless-slack serverless.yml"
    )

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(CACHE_USERS_TABLE)


# SOCLESS_INTERNAL
def handle_state(slack_profile_key="display_name", token=""):
    """Update the dynamoDB table with slack user's usernames and slack_ids
    Args:
        slack_profile_key: name in user profile to use for cache mapping
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
    helper = SlackHelper(token)

    paginate = True
    next_cursor = ""
    formatted_users = []
    while paginate:
        resp = helper.client.users_list(
            cursor=next_cursor, limit=1000, include_locale="false"
        )
        data = resp.data  # type: ignore
        next_cursor = resp.data["response_metadata"].get("next_cursor", "")  # type: ignore
        if not next_cursor:
            paginate = False
        formatted_users = formatted_users + [
            {"username": i["profile"][slack_profile_key], "slack_id": i["id"]}
            for i in data["members"]
            if i["profile"][slack_profile_key]
        ]

    with table.batch_writer() as writer:
        for item in formatted_users:
            writer.put_item(Item=item)

    return {"finished": True}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
