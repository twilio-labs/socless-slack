from socless import socless_bootstrap
import os
from slack_helpers import slack_client


def handle_state(channel_name, user_ids=[], is_private=False):
    """Create slack channel and invite any provided slack_ids.
    Args:
        channel_name (str): The name of channel to be created.
        user_ids (list) : slack_ids of users invited to new channel. Private Channels require a user.
        is_private (boolean): if the channel is private.
    Token_Type: xoxp (slack legacy user token)
    Note:
        - See https://api.slack.com/methods/conversations.create for more details on how to create private channel
    """

    if isinstance(user_ids, str):
        user_ids = user_ids.split(",")

    create_response = slack_client.conversations_create(
        name=channel_name, is_private=is_private, user_ids=user_ids
    )

    created_channel_id = create_response["channel"]["id"]
    bot_user_id = create_response["channel"]["creator"]

    if user_ids:
        user_ids = [x.strip() for x in user_ids if x != bot_user_id]

        invite_response = slack_client.conversations_invite(
            channel=created_channel_id, users=user_ids
        )

    return {
        "ok": True,
        "created_channel_id": created_channel_id,
        "channel_name": channel_name,
        "added_users": user_ids,
    }


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)