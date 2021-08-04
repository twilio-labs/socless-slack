from socless import socless_bootstrap
from slack_helpers import SlackHelper


def handle_state(channel_id, user_id="", user_ids=[], token=""):
    """Add users to a channel. Requires a Slack User Token (Token_Type: xoxp)
    Args:
        channel_id (str): Id of channel to invite.
        user_id (str) : [deprecated] single id of user to invite. Ex. W1234567
        user_ids (list): list of slack user_ids id to invite. Ex. [W12345, U12348]
    Returns:
        ok : (bool) true if user was added
        created_channel_id : (string) id of the channel

    Note:
        Token_Type: xoxp
        - See https://api.slack.com/methods/conversations.invite
    """
    helper = SlackHelper(token)

    if isinstance(user_ids, str):
        user_ids = [user_ids]

    if user_id:
        user_ids.append(user_id)

    _ = helper.client.conversations_invite(channel=channel_id, users=user_ids)

    return {"ok": True, "user_ids": user_ids}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
