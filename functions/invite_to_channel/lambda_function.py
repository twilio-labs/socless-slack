from socless import *
import slack
import os

def handle_state(channel_id, user_id):
    """Add people to the channel.
    Args:
        channel_id (str): Id of channel to invite.
        user_id (str):  user id to invite.
    Token_Type: xoxp
    Note:
        - See https://api.slack.com/methods/conversations.invite for more details on how to create private channel
    """

    SOCLESS_USER_TOKEN = os.environ['SOCLESS_USER_TOKEN']
    slack_api_client = slack.WebClient(SOCLESS_USER_TOKEN)
    try:
        res = slack_api_client.conversations_invite(channel=channel_id, users=[user_id])
        created_channel_id = res["channel"]['id']
        return {
            "ok": True,
            "created_channel_id": created_channel_id
        }
    except Exception as e:
        err_msg =f"{str(e.__class__)} {str(e)}"
        if res:
            err_msg = f"{err_msg} {str(res)}"

        return {
            "ok": False,
            "error": err_msg
        }


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
