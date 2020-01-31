from socless import *
import os
import slack


def handle_state(channel_name, user_ids, is_private=False):
    """ Create slack channel
    Args:
        channel_name (str): The name of channel to be created.
        user_ids (list) : list of all users to be added to channel.
        is_private (boolean): if the channel is private.
    Token_Type: xoxp (slack legacy user token)
    Note:
        - See https://api.slack.com/methods/conversations.create for more details on how to create private channel
    """

    if isinstance(user_ids, str):
        user_ids = [ user_ids ]

    SOCLESS_USER_TOKEN = os.environ['SOCLESS_USER_TOKEN']
    slack_api_client = slack.WebClient(SOCLESS_USER_TOKEN)

    try:
        res = slack_api_client.conversations_create(
            name=channel_name,
            is_private=is_private,
            user_ids=user_ids
        )

        print(res)

        created_channel_id = res["channel"]['id']
        return {
            "ok": True,
            "created_channel_id": created_channel_id,
            "channel_name": channel_name
        }
    except Exception as e:
        s = str(e)
        err_msg = s.split("'detail': ", 1)[1]
        err_msg = err_msg[:len(err_msg) - 1]
        return {
            "ok": False,
            "error": err_msg
        }


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
