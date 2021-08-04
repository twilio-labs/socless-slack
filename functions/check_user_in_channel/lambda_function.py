from socless import socless_bootstrap
from slack_helpers import paginated_api_call, SlackHelper


def handle_state(user_id: str, target_channel_id: str, token=""):
    """Check if user is in a particular slack channel.
    Args:
        user_id: user id of the user invoking the slash command
        target_channel_id: the channel id to be checked if user is in
    Returns:
        ok: (bool) True if user is found in the channel
    """

    helper = SlackHelper(token)

    response = paginated_api_call(
        api_method=helper.client.conversations_members,
        response_objects_name="members",
        channel=target_channel_id,
    )

    if user_id in response:
        return {"ok": True}

    return {"ok": False}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
