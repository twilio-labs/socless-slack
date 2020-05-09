from socless import socless_bootstrap
import os
import slack

SOCLESS_USER_TOKEN = os.environ["SOCLESS_USER_TOKEN"]
slack_api_client = slack.WebClient(SOCLESS_USER_TOKEN)


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
        user_ids = [user_ids]

    try:
        response = slack_api_client.conversations_create(
            name=channel_name, is_private=is_private, user_ids=user_ids
        )
        print(response)
        created_channel_id = response["channel"]["id"]

        return {
            "ok": True,
            "created_channel_id": created_channel_id,
            "channel_name": channel_name,
            "added_users": user_ids,
        }
    except Exception as e:
        s = str(e)
        return {"ok": False, "error": s}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
