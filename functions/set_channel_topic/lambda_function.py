from socless import socless_bootstrap
from slack_helpers import SlackHelper


def handle_state(channel_id: str, topic: str, token=""):
    """Set topic for a channel.
    Args:
        channel_id : channel_id for the targeted channel
        topic      : topic to set to channel
        token      : you can pass an alternate token via Jinja template in playbook.json (ssm, environment, etc)

    Returns:
        ok : (bool) True if topic was changed
    """
    helper = SlackHelper(token)

    _ = helper.client.conversations_setTopic(channel=channel_id, topic=topic)

    return {"ok": True, "topic": topic}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
