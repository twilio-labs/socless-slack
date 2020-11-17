from socless import *
from slack_helpers import slack_client, find_user, get_channel_id
import slack


def handle_state(context, message_template, target, target_type, as_user=True):
    """
    Send a Slack message without expecting a response
    """
    if not all([target_type, target, message_template]):
            raise Exception("Incomplete parameters supplied. Please supply target, target_type and message_template")

    target_id = get_channel_id(target, target_type)
    message = socless_template_string(message_template, context)
    resp = slack_client.chat_postMessage(channel=target_id, text=message, as_user=as_user)
    return {"response": resp.data, "slack_id": target_id}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state, include_event=True)
