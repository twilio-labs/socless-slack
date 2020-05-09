from socless import socless_bootstrap
import slack
import os


def handle_state(channel_id, user_id="", user_ids=[]):
    """Add people to the channel.
        Args:
            channel_id (str): Id of channel to invite.
            user_id (str) : [deprecated] single id of user to invite. Ex. W1234567
            user_ids (list): list of slack user_ids id to invite. Ex. [W12345, U12348]
        Note:
            Token_Type: xoxp
            - See https://api.slack.com/methods/conversations.invite for more details on how to create private channel
        """
    SOCLESS_USER_TOKEN = os.environ["SOCLESS_USER_TOKEN"]
    slack_api_client = slack.WebClient(SOCLESS_USER_TOKEN)

    if isinstance(user_ids, str):
        user_ids = [user_ids]

    if user_id:
        user_ids.append(user_id)

    try:
        res = slack_api_client.conversations_invite(channel=channel_id, users=user_ids)
        created_channel_id = res["channel"]["id"]
        return {"ok": True, "created_channel_id": created_channel_id}
    except Exception as e:
        s = str(e)
        return {"ok": False, "error": s}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
