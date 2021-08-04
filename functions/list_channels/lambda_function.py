from socless import socless_bootstrap
from slack_helpers import paginated_api_call, SlackHelper


def handle_state(token=""):
    """Returns a list of all available channels in the workspace.
    Returns:
        channels: (list) list of all channels
    Note: https://api.slack.com/methods/conversations.list
    """
    helper = SlackHelper(token)

    response = paginated_api_call(
        api_method=helper.client.conversations_list,
        response_objects_name="channels",
        exclude_archived=0,
        types="public_channel, private_channel",
    )
    return {"channels": response}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
