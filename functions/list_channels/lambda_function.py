from socless import socless_bootstrap
from slack_helpers import slack_client, paginated_api_call


def handle_state():
    """Returns a list of all available channels in the workspace.
    Returns:
        channels: (list) list of all channels
    Note: https://api.slack.com/methods/conversations.list
    """

    response = paginated_api_call(
        api_method=slack_client.conversations_list,
        response_objects_name="channels",
        exclude_archived=0,
        types="public_channel, private_channel",
    )
    return {"channels": response}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
