from socless import *
import os
import slack


def handle_state(channel_name, is_private):
    """Create private or public slack channel.
    Args:
        channel_name (str): The name of channel to be created.
        is_private (boolean): if the channel private
    Token_Type: xoxp
    Note:
        - See https://api.slack.com/methods/conversations.create for more details on how to create private channel
    """

    SOCLESS_USER_TOKEN = os.environ['SOCLESS_USER_TOKEN']
    slack_api_client = slack.WebClient(SOCLESS_USER_TOKEN)

    try:
        res = slack_api_client.conversations_create(
            name=channel_name,
            is_private=is_private
        )
        created_channel_id = res["channel"]['id']
        return {
            "ok": True,
            "created_channel_id": created_channel_id,
            "channel_name": channel_name
        }
    except Exception as e:
        print(e)
        err_msg =f"{str(e.__class__)} + {str(e)}"
        if res:
            err_msg = f"{err_msg} {str(res)}"
        return {
            "ok": False,
            "error": err_msg
        }


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
