from typing import List
from socless import socless_bootstrap
from slack_helpers import SlackHelper


def handle_state(
    channel_name: str,
    user_ids: List[str] = [],
    is_private: bool = False,
    token: str = "",
):
    """Create slack channel and invite any provided slack_ids.
    Args:
        channel_name : The name of channel to be created.
        user_ids     : slack_ids of users invited to new channel. Private Channels require a user.
        is_private   : if the channel is private.
        token        : you can pass an alternate token via Jinja template in playbook.json (ssm, environment, etc)
    Token_Type: xoxp (slack legacy user token)
    Note:
        - See https://api.slack.com/methods/conversations.create for more details on how to create private channel
    """
    helper = SlackHelper(token)

    if isinstance(user_ids, str):
        user_ids = user_ids.split(",")

    create_response = helper.client.conversations_create(
        name=channel_name, is_private=is_private, user_ids=user_ids
    )

    created_channel_id = create_response["channel"]["id"]  # type: ignore
    bot_user_id = create_response["channel"]["creator"]  # type: ignore

    if user_ids:
        user_ids = [x.strip() for x in user_ids if x != bot_user_id]

        _ = helper.client.conversations_invite(
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
