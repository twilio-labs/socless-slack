from socless import socless_bootstrap, socless_template_string
from slack_helpers import slack_client, find_user, get_channel_id
import slack


def handle_state(context, target, target_type, message_template):
    """Send a Slack message.
    Args:
        target:           (str) The name of the channel / name of user / slack id of channel/user
        target_type:      (str) The Channel type, either "user" or "channel" or "slack_id"
        message_template: (str) [optional] The 'text' field you want to send
    Returns:
    """
    if not all([target_type, target, message_template]):
        raise Exception(
            "Incomplete parameters supplied. Please supply target, target_type and message_template"
        )

    target_id = get_channel_id(target, target_type)
    message = socless_template_string(message_template, context)
    resp = slack_client.chat_postMessage(channel=target_id, text=message, as_user=True)
    return {"response": resp.data, "slack_id": target_id}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state, include_event=True)
