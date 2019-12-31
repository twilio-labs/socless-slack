from socless import *
from slack_helpers import slack_client, paginated_api_call


def handle_state():
    """
    Compiles list of all available channels
    :return: list of channels
    Note: https://api.slack.com/methods/conversations.list
    """
    ret = paginated_api_call(slack_client.conversations_list,
                             "channels",
                             exclude_archived=0,
                             types="public_channel, private_channel"
                             )
    return {
        "channels": ret
    }


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
