from typing import List
from socless import socless_bootstrap
from slack_helpers import SlackHelper


def handle_state(
    channel_id: str, user_id: str = "", user_ids: List[str] = [], token: str = ""
):
    """Add users to a channel. Requires a Slack User Token (Token_Type: xoxp)
    Args:
        channel_id : Id of channel to invite.
        user_id    : [deprecated] single id of user to invite. Ex. W1234567
        user_ids   : list of slack user_ids id to invite. Ex. [W12345, U12348]
        token      : you can pass an alternate token via Jinja template in playbook.json (ssm, environment, etc)
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
